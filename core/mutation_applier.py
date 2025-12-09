"""Applies mutations to source files - PLATFORM INDEPENDENT"""

import shutil
import random
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
import hashlib
from config.settings import DEFECTS4J_EXECUTABLE


class MutationApplier:
    """Handles mutation application to source files and unique mutant generation"""
    
    def __init__(self, random_seed: int = 42):
        self.random_seed = random_seed
        self.generated_combinations = set()
        # Initialize local random generator with seed
        self.rng = random.Random(random_seed)
    
    @staticmethod
    def find_java_file_by_class(class_name: str, source_dirs: List[Path]) -> Optional[Path]:
        """Find Java file by class name across source directories - PLATFORM INDEPENDENT"""
        # Use platform-independent path construction
        file_rel_path = Path(*class_name.split('.')) / f"{class_name.split('.')[-1]}.java"
        
        for src_dir in source_dirs:
            # Try direct path
            direct_path = src_dir / file_rel_path
            if direct_path.exists():
                return direct_path
            
            # Try common Maven structures - platform independent
            for prefix in [Path("src/main/java"), Path("src/java")]:
                maven_path = src_dir / prefix / file_rel_path
                if maven_path.exists():
                    return maven_path
        
        # Fallback: search recursively (slower but platform independent)
        for src_dir in source_dirs:
            class_file_name = f"{class_name.split('.')[-1]}.java"
            for java_file in src_dir.rglob(class_file_name):
                return java_file
        
        return None
    
    @staticmethod
    def apply_mutation_to_file(source_file: Path, line_number: int, 
                             original_code: str, mutated_code: str) -> bool:
        """Apply mutation to a specific file"""
        try:
            if not source_file.exists():
                return False
            
            with open(source_file, 'r') as f:
                lines = f.readlines()
            
            if line_number < 1 or line_number > len(lines):
                return False
            
            target_line_index = line_number - 1
            original_line = lines[target_line_index]
            
            # Try exact replacement
            if original_code in original_line:
                mutated_line = original_line.replace(original_code, mutated_code)
                lines[target_line_index] = mutated_line
            
            # Try with stripped whitespace
            elif original_code.strip() in original_line.strip():
                stripped_original = original_code.strip()
                stripped_line = original_line.strip()
                
                if stripped_original in stripped_line:
                    start_idx = original_line.find(stripped_original)
                    if start_idx != -1:
                        end_idx = start_idx + len(stripped_original)
                        before = original_line[:start_idx]
                        after = original_line[end_idx:]
                        mutated_line = before + mutated_code + after
                        lines[target_line_index] = mutated_line
            else:
                return False
            
            # Write the modified content back
            with open(source_file, 'w') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error applying mutation: {e}")
            return False
    
    def apply_multiple_mutations(self, source_file: Path, mutations: List[Dict]) -> bool:
        """Apply multiple mutations to a single file"""
        try:
            if not source_file.exists():
                return False
            
            with open(source_file, 'r') as f:
                lines = f.readlines()
            
            # Sort mutations by line number (descending) to avoid line number shifts
            mutations_sorted = sorted(mutations, key=lambda x: x['line_number'], reverse=True)
            
            for mutation in mutations_sorted:
                line_number = mutation['line_number']
                original_code = mutation['original_code']
                mutated_code = mutation['mutated_code']
                
                if line_number < 1 or line_number > len(lines):
                    continue
                
                target_line_index = line_number - 1
                original_line = lines[target_line_index]
                
                # Apply mutation
                if original_code in original_line:
                    mutated_line = original_line.replace(original_code, mutated_code)
                    lines[target_line_index] = mutated_line
                elif original_code.strip() in original_line.strip():
                    stripped_original = original_code.strip()
                    stripped_line = original_line.strip()
                    
                    if stripped_original in stripped_line:
                        start_idx = original_line.find(stripped_original)
                        if start_idx != -1:
                            end_idx = start_idx + len(stripped_original)
                            before = original_line[:start_idx]
                            after = original_line[end_idx:]
                            mutated_line = before + mutated_code + after
                            lines[target_line_index] = mutated_line
            
            # Write all changes at once
            with open(source_file, 'w') as f:
                f.writelines(lines)
            
            return True
            
        except Exception as e:
            print(f"Error applying multiple mutations: {e}")
            return False
    
    def create_project_copy(self, original_dir: Path, copy_dir: Path) -> bool:
        """Create a fast copy of the project (ignoring heavy artifacts)"""
        if copy_dir.exists():
            shutil.rmtree(copy_dir)
        
        try:
            shutil.copytree(
                original_dir, 
                copy_dir, 
                ignore=shutil.ignore_patterns('.git', 'mutants.log', '*.tar.gz')
            )
            return True
        except Exception as e:
            print(f"Error creating project copy: {e}")
            return False
    
    def generate_unique_mutants(self, all_mutations: List[Dict], num_mutants: int, 
                              max_mutations: int) -> List[Dict]:
        """
        Generate unique mutant combinations by selecting 1 to max_mutations mutations
        No two mutants should have the exact same set of mutations
        """
        unique_mutants = []
        attempts = 0
        max_attempts = num_mutants * 100  # Prevent infinite loops
        
        while len(unique_mutants) < num_mutants and attempts < max_attempts:
            attempts += 1
            
            # Randomly decide how many mutations for this mutant (1 to max_mutations)
            # Use the instance-local RNG so two appliers with the same seed produce
            # identical results and are not affected by global RNG state.
            num_mutations_for_mutant = self.rng.randint(1, max_mutations)

            # Randomly select mutations using the instance RNG
            selected_mutations = self.rng.sample(all_mutations, min(num_mutations_for_mutant, len(all_mutations)))
            
            # Create a unique signature for this combination
            mutation_signature = self._create_mutation_signature(selected_mutations)
            
            # Check if this combination is unique
            if mutation_signature not in self.generated_combinations:
                self.generated_combinations.add(mutation_signature)
                
                # Create a mutant info dict with all selected mutations
                mutant_info = {
                    'mutant_id': f"mutant_{len(unique_mutants) + 1}",
                    'mutations': selected_mutations,
                    'num_mutations': len(selected_mutations),
                    'mutators': [m['mutator'] for m in selected_mutations],
                    'signature': mutation_signature
                }
                
                # For compatibility with existing code, also include the first mutation's details
                # Include details from all mutations
                if selected_mutations:
                    mutant_info.update({
                        'mutator': ', '.join([m['mutator'] for m in selected_mutations]),
                        'class_name': ', '.join([m['class_name'] for m in selected_mutations]),
                        'line_number': ', '.join([str(m['line_number']) for m in selected_mutations]),  # ← All lines
                        'original_code': ' | '.join([m['original_code'] for m in selected_mutations]),
                        'mutated_code': ' | '.join([m['mutated_code'] for m in selected_mutations])
                    })
                
                unique_mutants.append(mutant_info)
        
        if len(unique_mutants) < num_mutants:
            print(f"Warning: Could only generate {len(unique_mutants)} unique mutants out of requested {num_mutants}")
        
        return unique_mutants
    

    def _create_mutation_signature(self, mutations: List[Dict]) -> str:
        """Create a unique signature for a set of mutations"""
        # Sort mutations by line number and class for consistent signatures
        sorted_mutations = sorted(mutations, key=lambda x: (x['class_name'], x['line_number']))
        
        signature_parts = []
        for mutation in sorted_mutations:
            part = f"{mutation['class_name']}:{mutation['line_number']}:{mutation['mutator']}"
            signature_parts.append(part)
        
        signature = "|".join(signature_parts)
        
        # Use hash to make it shorter (optional)
        return signature
    #hashlib.md5(signature.encode()).hexdigest()