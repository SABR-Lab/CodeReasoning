import xml.etree.ElementTree as ET
import re

def parse_jvm_signature(signature):
    """
    Translates JVM signatures (e.g., (DD)V) into human-readable parameter lists.
    """
    # Mapping of JVM primitive descriptors to Java types
    mapping = {
        'Z': 'boolean',
        'B': 'byte',
        'C': 'char',
        'S': 'short',
        'I': 'int',
        'J': 'long',
        'F': 'float',
        'D': 'double',
        'V': 'void'
    }
    
    # Extract the part between parentheses
    params_match = re.search(r'\((.*?)\)', signature)
    if not params_match:
        return "()"
    
    params_str = params_match.group(1)
    decoded_params = []
    
    i = 0
    while i < len(params_str):
        char = params_str[i]
        
        # Handle Arrays
        prefix = ""
        while char == '[':
            prefix += "[]"
            i += 1
            char = params_str[i]
            
        # Handle Objects (L...;)
        if char == 'L':
            end = params_str.find(';', i)
            obj_path = params_str[i+1:end]
            # Get only the class name, not the full package
            obj_name = obj_path.split('/')[-1]
            decoded_params.append(f"{obj_name}{prefix}")
            i = end + 1
        # Handle Primitives
        elif char in mapping:
            decoded_params.append(f"{mapping[char]}{prefix}")
            i += 1
        else:
            i += 1 # Safety increment

    return f"({', '.join(decoded_params)})"

def translate_coverage_xml(xml_content):
    root = ET.fromstring(xml_content)
    
    print(f"{'XML Method Name':<30} | {'Java Translation':<40} | {'Line Range'}")
    print("-" * 90)

    for package in root.findall(".//package"):
        for cls in package.findall(".//class"):
            full_class_name = cls.get('name')
            simple_class_name = full_class_name.split('.')[-1]
            
            for method in cls.findall(".//methods/method"):
                name = method.get('name')
                sig = method.get('signature')
                
                # 1. Translate the Method Name
                if name == "<init>":
                    translated_name = simple_class_name  # Constructor
                elif name == "<clinit>":
                    translated_name = "static initializer"
                else:
                    translated_name = name
                
                # 2. Translate the Signature
                readable_sig = parse_jvm_signature(sig)
                
                # 3. Get Line Numbers (for verification)
                lines = method.findall("./lines/line")
                if lines:
                    line_numbers = [int(l.get('number')) for l in lines]
                    line_range = f"L{min(line_numbers)}-L{max(line_numbers)}"
                else:
                    line_range = "No lines"

                display_xml = f"{name} {sig}"
                display_java = f"{translated_name}{readable_sig}"
                
                print(f"{display_xml:<30} | {display_java:<40} | {line_range}")

# The coverage.xml content you provided
xml_data = """[PASTE YOUR XML CONTENT HERE]"""

# If running locally, you can load from file:
# with open('coverage.xml', 'r') as f:
#     xml_data = f.read()

translate_coverage_xml(xml_data)