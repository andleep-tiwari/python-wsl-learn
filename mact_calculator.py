import streamlit as st
import re
from datetime import date
from num2words import num2words

def calculate_compensation(age, monthly_income, dependent_count, accident_type):
    annual_income = monthly_income * 12
    
    # Multiplier method as per Supreme Court guidelines
    if age <= 15:
        multiplier = 15
    elif age <= 20:
        multiplier = 18
    elif age <= 25:
        multiplier = 16
    elif age <= 30:
        multiplier = 15
    elif age <= 35:
        multiplier = 14
    elif age <= 40:
        multiplier = 13
    elif age <= 45:
        multiplier = 11
    elif age <= 50:
        multiplier = 9
    else:
        multiplier = 6

    components = []
    total = 0

    if accident_type == "Fatal":
        # Loss of dependency (as per dependency ratio)
        dependency_ratio = 0.5 if dependent_count <= 2 else (0.6 if dependent_count <= 4 else 0.7)
        loss_of_dependency = annual_income * dependency_ratio * multiplier
        consortium = 40000 * dependent_count
        funeral_expenses = 15000
        loss_of_estate = 15000
        
        total = loss_of_dependency + consortium + funeral_expenses + loss_of_estate
        
        components = [
            f"1. Loss of Dependency: Rs. {loss_of_dependency:,.2f}",
            f"   - Annual Income: Rs. {annual_income:,.2f}",
            f"   - Dependency Ratio: {dependency_ratio}",
            f"   - Multiplier: {multiplier}",
            f"2. Consortium: Rs. {consortium:,.2f}",
            f"3. Funeral Expenses: Rs. {funeral_expenses:,.2f}",
            f"4. Loss of Estate: Rs. {loss_of_estate:,.2f}"
        ]
        
    else:  # Injury
        medical_expenses = st.number_input("Medical Expenses (Rs.)", min_value=0, value=0)
        months_loss = st.number_input("Months of Income Loss", min_value=0, value=0)
        loss_of_income = monthly_income * months_loss
        
        components = [
            f"1. Medical Expenses: Rs. {medical_expenses:,.2f}",
            f"2. Loss of Income: Rs. {loss_of_income:,.2f}"
        ]
        
        total = medical_expenses + loss_of_income
        
        if st.checkbox("Permanent Disability"):
            disability_percentage = st.number_input("Disability Percentage", min_value=0, max_value=100, value=0)
            permanent_disability = annual_income * multiplier * (disability_percentage/100)
            total += permanent_disability
            components.append(f"3. Permanent Disability Compensation: Rs. {permanent_disability:,.2f}")
            components.append(f"   - Annual Income: Rs. {annual_income:,.2f}")
            components.append(f"   - Multiplier: {multiplier}")
            components.append(f"   - Disability: {disability_percentage}%")
    
    return total, "\n".join(components)

def load_template(template_path):
    try:
        with open(template_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return None

def fill_template(template, variables_dict):
    filled_template = template
    for key, value in variables_dict.items():
        filled_template = filled_template.replace(f"{{{{ {key} }}}}", str(value))
    return filled_template

def main():
    st.title("Motor Accident Claims Tribunal Calculator")
    
    # Basic case information
    col1, col2 = st.columns(2)
    with col1:
        court_location = st.text_input("Court Location")
        case_number = st.text_input("Case Number")
        case_year = st.text_input("Case Year")
        
    with col2:
        claimant_name = st.text_input("Claimant Name")
        respondent_name = st.text_input("Respondent Name")
        victim_name = st.text_input("Victim Name")

    # Accident details
    accident_type = st.radio("Type of Accident", ["Fatal", "Injury"])
    accident_date = st.date_input("Date of Accident")
    
    # Victim details
    col3, col4 = st.columns(2)
    with col3:
        age = st.number_input("Age of Victim", min_value=1, max_value=100)
        monthly_income = st.number_input("Monthly Income (Rs.)", min_value=0)
        
    with col4:
        dependent_count = st.number_input("Number of Dependents", min_value=0)
        occupation_type = st.selectbox("Occupation Type", 
                                     ["Government Service", "Private Service", "Self-Employed"])

    if st.button("Calculate Compensation"):
        total_compensation, compensation_details = calculate_compensation(
            age, monthly_income, dependent_count, accident_type
        )
        
        template_content = load_template('./mact_template.txt')
        if template_content is None:
            st.error("Template file not found!")
            return
            
        variables = {
            'court_location': court_location,
            'case_number': case_number,
            'case_year': case_year,
            'claimant_name': claimant_name,
            'respondent_name': respondent_name,
            'date': date.today().strftime("%d-%m-%Y"),
            'accident_type': accident_type,
            'victim_name': victim_name,
            'age': age,
            'accident_date': accident_date.strftime("%d-%m-%Y"),
            'monthly_income': f"{monthly_income:,.2f}",
            'occupation_type': occupation_type,
            'dependent_count': dependent_count,
            'compensation_details': compensation_details,
            'total_compensation': f"{total_compensation:,.2f}",
            'compensation_in_words': num2words(int(total_compensation), lang='en_IN').title()
        }
        
        filled_judgment = fill_template(template_content, variables)
        
        st.markdown("### Generated Judgment")
        st.markdown(filled_judgment)
        
        st.download_button(
            label="Download Judgment",
            data=filled_judgment,
            file_name=f"judgment_mact_{case_number}_{case_year}.txt",
            mime="text/plain"
        )

if __name__ == "__main__":
    main()