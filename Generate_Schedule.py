import streamlit as st
import pandas as pd
import re

# --- Core Logic ---
def get_lab_status(course, room):
    c, r = str(course).upper(), str(room).upper()
    # Identifying labs by course name or codes
    lab_keywords = ["LAB", "COAL", "PRACTICAL", "STUDIO", "WORKSHOP", "COMPUTER", "CSCL"]
    is_lab_class = any(kw in c for kw in lab_keywords) or c.endswith("-L")
    is_lab_room = "LAB" in r or "WORKSHOP" in r or "STUDIO" in r
    return is_lab_class, is_lab_room

def process_schedule(df):
    all_rows = []
    curr_sect, curr_dt = "General", "N/A"

    for i in range(len(df)):
        row = [str(x).strip() for x in df.iloc[i].values]
        if not any(row): continue

        if row[0].upper().startswith("SECTION:"):
            curr_sect = row[0].replace("SECTION:", "").strip()
        elif " | " in row[0]:
            curr_dt = row[0]
        elif row[0] == "Course:":
            crs = row[1]
            inst, rm, bld = "", "", ""
            
            # Extract details from blocks
            if i + 1 < len(df):
                r1 = [str(x).strip() for x in df.iloc[i+1].values]
                if r1[0] == "Instructor:": inst = r1[1]
                for idx, v in enumerate(r1):
                    if "Room:" in v and idx+1 < len(r1): rm = r1[idx+1]
            if i + 2 < len(df):
                r2 = [str(x).strip() for x in df.iloc[i+2].values]
                if r2[0] == "Building:": bld = r2[1]

            # Flatten data: Keep Section and Instructor on every row
            all_rows.append({
                "Section": curr_sect,
                "Day_Time": curr_dt,
                "Course": crs,
                "Instructor": inst if inst else "To Be Assigned",
                "Room": rm,
                "Building": bld
            })

    final_df = pd.DataFrame(all_rows)
    
    # Lab Swap Logic: Find labs in theory rooms and swap with theory in labs
    tags = final_df.apply(lambda x: get_lab_status(x['Course'], x['Room']), axis=1)
    final_df['is_l_c'], final_df['is_l_r'] = [t[0] for t in tags], [t[1] for t in tags]

    for time in final_df['Day_Time'].unique():
        idx = final_df[final_df['Day_Time'] == time].index
        mismatched_labs = [i for i in idx if final_df.at[i, 'is_l_c'] and not final_df.at[i, 'is_l_r']]
        spare_lab_rooms = [i for i in idx if not final_df.at[i, 'is_l_c'] and final_df.at[i, 'is_l_r']]
        
        for l_idx, r_idx in zip(mismatched_labs, spare_lab_rooms):
            final_df.at[l_idx, 'Room'], final_df.at[r_idx, 'Room'] = final_df.at[r_idx, 'Room'], final_df.at[l_idx, 'Room']

    return final_df[['Section', 'Day_Time', 'Course', 'Instructor', 'Room', 'Building']]

# --- Streamlit UI ---
st.set_page_config(page_title="Schedule Optimizer", layout="wide")
st.title("🧩 Master Schedule Lego Optimizer")

uploaded_file = st.file_uploader("Upload Master Schedule CSV", type="csv")

if uploaded_file:
    # low_memory=False prevents the mixed types error you saw
    df_raw = pd.read_csv(uploaded_file, header=None, low_memory=False).fillna("")
    
    if st.button("Fix Sections & Labs"):
        with st.spinner("Processing large dataset..."):
            result = process_schedule(df_raw)
            st.success(f"Optimized {len(result)} class entries!")
            
            # Show top 50 rows for verification
            st.dataframe(result.head(50), use_container_width=True)
            
            csv = result.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Download Final Schedule", data=csv, file_name="FIXED_SCHEDULE.csv")