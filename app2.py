import streamlit as st
import pandas as pd
import re


# Load the data
uom = pd.read_csv("uom.csv")
location = pd.read_csv("indianDistrictsList.csv")
prepositions = pd.read_csv("prepositions_updated.csv")['prepositions'].tolist()
shortCodes = pd.read_csv("shortCodesProduct.csv")
procurement = pd.read_csv("procurementTerms.csv")
product_df = pd.read_csv("Updated_keywordProductSynonym.csv")
product_df['synonymkeyword'] = product_df['synonymkeyword'].fillna('')
company_df = pd.read_csv("Copy of company_list_with_abbr.csv")
stop_words = pd.read_csv("stop_words.csv")

def textSegmentation(input_text):
    result_dict={}
    units = set()
    for word in input_text.split():
        if any(uom['units'].str.contains(fr"\b{word}\b", case=False, regex=True)):
            units.add(word)
    result_dict['units'] = units
    
    # extract locations from the cleaned text
    locations = set()
    for word in input_text.split():
        if any(location['Districts'].str.contains(fr"\b{word}\b", regex= True,case=False)):
            locations.add(word)
    result_dict['locations'] = locations

    procurementTerm = set()
    for word in input_text.split():
        if any(procurement['ProcurementTerms'].str.contains(fr"\b{word}\b", regex=True, case=False)):
            procurementTerm.add(word)
    result_dict['procurement Terms'] = procurementTerm   
    # return the dictionary of results
    return result_dict

def match_company(input_text):
    input_words = re.findall(r'[a-zA-Z]+', input_text)
    # initialize variables
    keyword_matches = []
    remaining_words = input_words
    # search for longest possible matching word strings in keyword column
    while len(remaining_words) > 0:
        for i in range(len(remaining_words), 0, -1):
            phrase = ' '.join(remaining_words[:i])
            matches = company_df[company_df['Abbrevation'].str.lower() == phrase.lower()]
            if len(matches) > 0:
                keyword_matches.append((matches.iloc[0]['companyrecno'], phrase))
                remaining_words = remaining_words[i:]
                break
        else:
            for i in range(len(remaining_words), 0, -1):
                phrase = ' '.join(remaining_words[:i])
                matches = company_df[company_df['CompanyName'].str.lower() == phrase.lower()]
                if len(matches) > 0:
                    keyword_matches.append((matches.iloc[0]['companyrecno'], phrase))
                    remaining_words = remaining_words[i:]
                    break
            else:
                # no match found in any column
                remaining_words.pop(0)
    # return keycodeids and corresponding phrases
    return keyword_matches

def search_keywords(input_text):
    # remove unwanted characters
    input_text = re.findall(r'[a-zA-Z]+', input_text)
    # remove stop words
    filtered_words = [word for word in input_text if word.lower() not in stop_words]
    # initialize variables
    keyword_matches = []
    remaining_words = filtered_words
    # search for longest possible matching word strings in keyword column
    while len(remaining_words) > 0:
        for i in range(len(remaining_words), 0, -1):
            phrase = ' '.join(remaining_words[:i])
            matches = product_df[product_df['keyword'].str.lower() == phrase.lower()]
            if len(matches) > 0:
                keyword_matches.append((matches.iloc[0]['keycodeid'], phrase))
                remaining_words = remaining_words[i:]
                break
        else:
            # no match found in keyword column, try synonym column
            for i in range(len(remaining_words), 0, -1):
                phrase = ' '.join(remaining_words[:i])
                matches = product_df[product_df['synonymkeyword'].str.lower()==phrase.lower()]
                if len(matches) > 0:
                    keyword_matches.append((matches.iloc[0]['synonymId'], phrase))
                    remaining_words = remaining_words[i:]
                    break
            else:
                # no match found in synonym column, try productname column
                for i in range(len(remaining_words), 0, -1):
                    phrase = ' '.join(remaining_words[:i])
                    matches = product_df[product_df['ProductName'].str.lower()==phrase.lower()]
                    if len(matches) > 0:
                        keyword_matches.append((matches.iloc[0]['ProductCode'], phrase))
                        remaining_words = remaining_words[i:]
                        break
                else:
                    # no match found in any column
                    remaining_words.pop(0)
    # return keycodeids and corresponding phrases
    return keyword_matches

# Streamlit UI
st.title("TIGER AI")

# Get user input
input_text = st.text_input("Enter the search phrase:")

# if st.button("Segments Matching"):
#     # Call the textSegmentation function and display the results
#     result = textSegmentation(input_text)
#     st.write("Units: ", result['units'])
#     st.write("Locations: ", result['locations'])
#     st.write("Procurement Terms: ", result['procurement Terms'])

# if st.button("Looking for Company Name?"):
#     # Call the match_company function and display the results
#     result = match_company(input_text)
#     st.write("Keyword Matches: ", result)

# if st.button("Get Product Names"):
#     # Call the search_keywords function and display the results
#     result = search_keywords(input_text)
#     st.write("Keyword Matches: ", result)
    
if st.button("Get Results"):
    # Call all three functions and display the results
    segmentation_result = textSegmentation(input_text)
    company_result = match_company(input_text)
    product_result = search_keywords(input_text)

    st.write("Units: ", segmentation_result['units'])
    st.write("Locations: ", segmentation_result['locations'])
    st.write("Procurement Terms: ", segmentation_result['procurement Terms'])
    st.write("Company Name Matches: ", company_result)
    st.write("Product Name Matches: ", product_result)

