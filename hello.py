import streamlit as st
import re
from datetime import date

def load_template(template_path):
    try:
        with open(template_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

def extract_variables(template):
    # Find all {{ variable }} patterns in the template
    pattern = r'\{\{\s*(\w+)\s*\}\}'
    return list(set(re.findall(pattern, template)))

def fill_template(template, variables_dict):
    filled_template = template
    for key, value in variables_dict.items():
        filled_template = filled_template.replace(f"{{{{ {key} }}}}", value)
    return filled_template

def main():
    st.title("Template Generator")
    
    # Load template
    template_content = load_template('./template.txt')
    
    if template_content is None:
        st.error("Template file not found!")
        return
    
    # Extract variables from template
    variables = extract_variables(template_content)
    
    # Create input fields for each variable
    input_values = {}
    
    for var in variables:
        if var == 'date':  # Special handling for date
            input_values[var] = st.date_input(f"Enter {var}:", date.today()).strftime("%B %d, %Y")
        else:
            input_values[var] = st.text_input(f"Enter {var}:")
    
    if st.button("Generate"):
        if all(input_values.values()):  # Check if all fields are filled
            result = fill_template(template_content, input_values)
            
            # Display the result
            st.markdown("### Preview:")
            st.markdown(result)
            
            # Add download button
            st.download_button(
                label="Download as MD",
                data=result,
                file_name="generated_content.md",
                mime="text/markdown"
            )
        else:
            st.warning("Please fill all the fields!")

if __name__ == "__main__":
    main()