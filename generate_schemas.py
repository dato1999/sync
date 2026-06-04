import os
import glob
import sys

def main():
    type_mapping = {
        "integer": "Int",
        "double": "Double",
        "string": "String",
        "boolean": "Boolean"
    }

    # Location where the workflow clones the schema repo
    cfg_files = glob.glob("external-schemas/schemas/**/*.cfg", recursive=True)
    output_dir = "src/main/scala/com/example/schemas"

    if not cfg_files:
        print("Error: No .cfg files found in 'external-schemas/schemas/'")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    for cfg_path in cfg_files:
        base_name = os.path.splitext(os.path.basename(cfg_path))[0]
        class_name = base_name.capitalize()
        output_path = os.path.join(output_dir, f"{class_name}.scala")

        fields = []
        with open(cfg_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                
                if ":" in line:
                    name, data_type = line.split(":", 1)
                    scala_type = type_mapping.get(data_type.strip(), "String")
                    fields.append(f"  {name.strip()}: {scala_type}")

        case_class_content = "package com.example.schemas\n\n"
        case_class_content += f"case class {class_name}(\n"
        case_class_content += ",\n".join(fields)
        case_class_content += "\n)\n"

        with open(output_path, "w") as out:
            out.write(case_class_content)
            
        print(f"Successfully generated {output_path} from {cfg_path}")

if __name__ == "__main__":
    main()
