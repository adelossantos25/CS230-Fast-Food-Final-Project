"""
Name: Ania De Los Santos
CS230: Section 5
Data: fast_food_usa.csv
URL:        Link to your web application on Streamlit Cloud (if posted)

Description:

This program ... (a few sentences about your program and the queries and charts)
"""



import streamlit as st  # Import Streamlit for creating web apps
import pandas as pd  # Import pandas for data manipulation
import folium  # Import folium for creating interactive maps
from streamlit_folium import st_folium  # Integrate folium maps with Streamlit
import matplotlib.pyplot as plt  # Import matplotlib for plotting graphs

# Load Data
@st.cache_data  # Cache the function to improve performance on repeated calls
def load_df(filepath):
    try:
        df = pd.read_csv(filepath)  # Read the CSV file into a DataFrame
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")  # Display an error message if the file fails to load
        return None


df = load_df('fast_food_usa.csv')  # Call the function to load the data

# Clean and Manipulate Data
if df is not None:  # Check if the data was loaded successfully
    # Normalize column data
    df['categories'] = df['categories'].str.lower()  # Convert all category names to lowercase
    df['categories'] = df['categories'].str.replace(r"[,/]", " and ",
                                                    regex=True)  # Replace commas and slashes with " and "
    df['categories'] = df['categories'].str.replace(r"\s+and\s+", " and ", regex=True)  # Normalize "and" spacing
    df['categories'] = df['categories'].str.replace(r"\s+", " ", regex=True)  # Remove extra spaces
    df['city'] = df['city'].str.title()  # Capitalize city names
    df['province'] = df['province'].str.upper()  # Convert province names to uppercase
    # Define broader category mapping for partial matches
    category_map = {
        "Fast Food": ["fast food", "fast food restaurants", "fast food restaurant"],
        "Burger": ["burger", "burger joint", "burgers", "hamburgers"],
        "Mexican": ["mexican", "taco"],
        "Sandwiches": ["sandwich"],
        "Fried Chicken": ["fried chicken", "chicken"],
        "Ice Cream and Dessert": ["ice cream", "dessert"],
        "Bakery": ["bakery"],
        "Coffee & Tea": ["coffee", "tea"],
        "Breakfast": ["breakfast"],
        "Pizza": ["pizza"],
        "Hot Dogs": ["hot dog"],
        "Seafood": ["seafood"],
        "Asian": ["asian", "chinese", "japanese", "sushi"],
        "American": ["american"],
        "Middle Eastern": ["middle eastern"],
        "Mediterranean": ["mediterranean"],
        "Other": []  # Catch-all for uncategorized
    }


    def map_category(category, mapping):
        # Split normalized categories into individual tags
        split_categories = [c.strip() for c in category.split(" and ")]  # Split by 'and' and strip whitespace
        matched_categories = set()  # Store matched categories
        # Check each split category against the mapping
        for split in split_categories:
            for key, values in mapping.items():
                if any(value in split for value in values):  # If any value matches, add to the matched set
                    matched_categories.add(key)
        # Return matches or 'Other' if no matches found
        if matched_categories:
            return " & ".join(sorted(matched_categories))  # Sort for consistency
        return "Other"


    # Apply the category mapping function to the 'categories' column
    df['refined_category'] = df['categories'].apply(lambda x: map_category(x, category_map))

# Sidebar Customization
st.sidebar.markdown("## Your one-stop shop for fast food data! 🍟")
st.sidebar.markdown("By default, all restaurants are displayed. Use filters to refine your search.")  # Guidance text

# 1. Select Categories
selected_category = st.sidebar.multiselect("Select Categories",
                                           options=list(category_map.keys()))  # Multi-select for categories

# 2. Select Restaurant (dependent on filtered data)
if df is not None:
    # Filter the dataset by selected categories first
    filtered_restaurant_df = df.copy()
    if selected_category:
        filtered_restaurant_df = filtered_restaurant_df[
            filtered_restaurant_df['refined_category'].apply(lambda x: any(cat in x for cat in selected_category))
        ]

    # Get restaurant names from the filtered dataset
    restaurant_names = filtered_restaurant_df['name'].unique().tolist()
    restaurant_names.insert(0, "All Restaurants")  # Add "All Restaurants" option
    selected_restaurant = st.sidebar.selectbox("Select Restaurant", options=restaurant_names)
else:
    selected_restaurant = "All Restaurants"  # Default to "All Restaurants" if no data is loaded

# 3. Search by Province (instead of city)
selected_province = st.sidebar.text_input("Search by Province (Enter Initials)", "")  # Text input for province search

# 4. Number of Results Slider
num_results = st.sidebar.slider("Number of Results to Show", min_value=1, max_value=10001,
                                value=500)  # Slider for number of results

# Filter Data based on selected province
if df is not None:
    filtered_df = df.copy()  # Start with the full dataset

    # Apply category filter
    if selected_category:
        filtered_df = filtered_df[
            filtered_df['refined_category'].apply(lambda x: any(cat in x for cat in selected_category))
        ]

    # Apply restaurant filter
    if selected_restaurant and selected_restaurant != "All Restaurants":
        filtered_df = filtered_df[filtered_df['name'] == selected_restaurant]

    # Apply province filter
    if selected_province:
        filtered_df = filtered_df[
            filtered_df['province'].str.contains(selected_province, case=False, na=False)
        ]

    # Limit results
    filtered_df = filtered_df.head(num_results)
else:
    filtered_df = pd.DataFrame()  # Empty DataFrame if no data is available

# Fun Title Styling with HTML and CSS
st.markdown("""
    <style>
        .title {
            font-size: 40px;
            color: #FF5733;
            font-family: 'Comic Sans MS', cursive, sans-serif;
            text-shadow: 2px 2px #FFDDC1;
        }
        .sidebar {
            background-color: #FCE4EC;
        }
    </style>
    <div class="title">🎉 Welcome to the Fast Food Explorer! 🍔</div>
""", unsafe_allow_html=True)

# Create tabs for different views
tabs = st.tabs(["Map View", "Bar Chart", "Pie Chart", "Filtered Data"])

# Map View
with tabs[0]:
    if not filtered_df.empty:
        st.markdown("### Restaurant Map")  # Subtitle for the map
        m = folium.Map(location=[filtered_df['latitude'].mean(), filtered_df['longitude'].mean()], zoom_start=5)
        for _, row in filtered_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                radius=5,
                color='blue',
                fill=True,
                fill_color='blue',
                fill_opacity=0.6,
                tooltip=row['name']
            ).add_to(m)
        st_folium(m, width=700, height=500)

# Bar Chart
with tabs[1]:
    if not filtered_df.empty:
        st.markdown("### Top Cities by Restaurant Count")  # Subtitle for the bar chart
        top_cities = filtered_df['city'].value_counts().head(10)
        fig, ax = plt.subplots()
        top_cities.plot(kind='bar', ax=ax, color='skyblue', edgecolor='black')
        ax.set_title("Top Cities")
        ax.set_ylabel("Number of Restaurants")
        ax.set_xlabel("City")
        st.pyplot(fig)

# Pie Chart
with tabs[2]:
    if not filtered_df.empty:
        st.markdown("### Restaurant Distribution")  # Subtitle for the pie chart
        unique_provinces = filtered_df['province'].nunique()
        if unique_provinces == 1:
            city_counts = filtered_df['city'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(city_counts, labels=city_counts.index, autopct='%1.1f%%', startangle=90,
                   colors=plt.cm.Paired.colors)
            ax.set_title("City Distribution in Selected Province")
            st.pyplot(fig)
        else:
            province_counts = filtered_df['province'].value_counts()
            fig, ax = plt.subplots()
            ax.pie(province_counts, labels=province_counts.index, autopct='%1.1f%%', startangle=90,
                   colors=plt.cm.Paired.colors)
            ax.set_title("Province Distribution (Filtered)")
            st.pyplot(fig)

# Filtered Data
with tabs[3]:
    if not filtered_df.empty:
        st.markdown("### Filtered Restaurant Data")  # Subtitle for the data table
        display_columns = ["name", "city", "province", "refined_category"]
        st.dataframe(filtered_df[display_columns])

# Add a footer with custom style
st.markdown("""
    <style>
        .footer {
            text-align: center;
            font-size: 16px;
            color: #FF5733;
            font-weight: bold;
            margin-top: 40px;
        }
    </style>
    <div class="footer">Created with ❤️ by Ania De Los Santos</div>
""", unsafe_allow_html=True)

