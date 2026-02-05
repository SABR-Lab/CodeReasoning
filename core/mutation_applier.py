"""Applies mutations to source files - SIMPLIFIED & FIXED"""

import hashlib
import shutil
import random
from pathlib import Path
from typing import List, Optional, Dict, Any


class MutationApplier:
    """Handles mutation application - SIMPLIFIED for reliability"""
    
    def __init__(self, random_seed: int = 42, project_id: str = "", bug_id: str = ""):
        self.random_seed = random_seed
        self.project_id = project_id
        self.bug_id = bug_id
        
        # Simple deterministic seed based on inputs
        seed_value = random_seed
        if project_id and bug_id:
            # Simple deterministic calculation without hash()
            seed_str = f"{project_id}{bug_id}{random_seed}"
            seed_value = sum(ord(c) for c in seed_str) % (2**31)
        
        self.rng = random.Random(seed_value)
    
    def generate_unique_mutants(self, all_mutations: List[Dict], num_mutants: int, 
                              max_mutations: int) -> List[Dict]:
        """
        Generate unique mutants - SIMPLIFIED deterministic algorithm
        """
        # 1. Sort mutations for consistency
        sorted_mutations = sorted(all_mutations,
                                 key=lambda x: (x['class_name'],
                                               x['line_number'],
                                               x['mutator'],
                                               x['original_code']))
        
        # 2. Simple deterministic selection
        unique_mutants = []
        used_combinations = set()
        
        for mutant_num in range(1, num_mutants + 1):
            # Create seed for this mutant
            mutant_seed = self.random_seed + mutant_num * 1000
            
            # Determine number of mutations
            temp_rng = random.Random(mutant_seed)
            num_for_mutant = temp_rng.randint(1, max_mutations)
            
            # Select mutations
            selected = []
            for i in range(num_for_mutant):
                # Deterministic index selection
                idx = (mutant_seed + i * 17) % len(sorted_mutations)
                selected.append(sorted_mutations[idx])
            
            # Sort and create signature
            selected.sort(key=lambda x: (x['class_name'], x['line_number']))
            
            # Simple signature without hash()
            signature_parts = []
            for m in selected:
                part = f"{m['class_name']}:{m['line_number']}:{m['mutator']}"
                signature_parts.append(part)
            signature = "|".join(signature_parts)
            
            # Ensure uniqueness
            if signature in used_combinations:
                # Try alternative selection
                alt_seed = mutant_seed + 9999
                alt_rng = random.Random(alt_seed)
                num_for_mutant = alt_rng.randint(1, max_mutations)
                selected = []
                for i in range(num_for_mutant):
                    idx = (alt_seed + i * 23) % len(sorted_mutations)
                    selected.append(sorted_mutations[idx])
                
                selected.sort(key=lambda x: (x['class_name'], x['line_number']))
                signature_parts = []
                for m in selected:
                    part = f"{m['class_name']}:{m['line_number']}:{m['mutator']}"
                    signature_parts.append(part)
                signature = "|".join(signature_parts)
            
            if signature not in used_combinations:
                used_combinations.add(signature)
                
                combined_id = '|'.join([str(m.get('mutant_id', '')) for m in selected]) if selected else f"gen_{len(unique_mutants) + 1}"

                mutant_info = {
                    'mutant_id': combined_id,
                    'mutations': selected,
                    'num_mutations': len(selected),
                    'mutators': sorted([m['mutator'] for m in selected]),
                    'signature': signature,
                    'project_id': self.project_id,
                    'bug_id': self.bug_id,
                    'generation_seed': mutant_seed
                }
                
                if selected:
                    first = selected[0]
                    mutant_info.update({
                        'mutator': first['mutator'],
                        'class_name': first['class_name'],
                        'line_number': first['line_number'],
                        'original_code': first['original_code'],
                        'mutated_code': first['mutated_code']
                    })
                
                unique_mutants.append(mutant_info)
        
        print(f"Generated {len(unique_mutants)} unique mutants for {self.project_id}-{self.bug_id}")
        return unique_mutants
    
    # ... rest of the class methods remain the same ...
    
    def _create_mutation_signature(self, mutations: List[Dict], combined_id: str = "") -> str:
        """Create deterministic signature for mutations including combined_id"""
        parts = []
        
        # Include combined_id in signature
        if combined_id:
            parts.append(f"ID:{combined_id}")
        
        # Add mutation details
        for m in sorted(mutations, key=lambda x: (x.get('mutant_id', ''), 
                                                 x['class_name'], 
                                                 x['line_number'])):
            part = (f"{m.get('mutant_id', '')}:{m['class_name']}:{m['line_number']}:{m['mutator']}:"
                   f"{hashlib.md5(m['original_code'].encode()).hexdigest()[:8]}:"
                   f"{hashlib.md5(m['mutated_code'].encode()).hexdigest()[:8]}")
            parts.append(part)
        
        return "||".join(parts)
    
    @staticmethod
    def find_java_file_by_class(class_name: str, source_dirs: List[Path]) -> Optional[Path]:
        """Find Java file by class name across source directories"""
        file_rel_path = class_name.replace('.', '/') + '.java'
        
        for src_dir in source_dirs:
            # Try direct path
            direct_path = src_dir / file_rel_path
            if direct_path.exists():
                return direct_path
            
            # Try common Maven structures
            for prefix in ["src/main/java", "src/java"]:
                maven_path = src_dir / prefix / file_rel_path
                if maven_path.exists():
                    return maven_path
        
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