import pandas as pd
import os

DATA_PATH = r'dataset/Schedules/Year 2025/All Program Classes Schedule Fall 2025'

def scrape_everything():
    final_data = []
    print("🧹 Starting Deep Clean (Version 2.0)...")

    # Day and Time helpers
    days_of_week = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY']
    
    for file in os.listdir(DATA_PATH):
        if not file.endswith(('.xlsx', '.xls')): continue
            
        print(f"📂 Reading: {file}")
        path = os.path.join(DATA_PATH, file)
        
        try:
            # Handle both new and old Excel formats
            xls = pd.ExcelFile(path)
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(path, sheet_name=sheet_name).fillna("")
                
                current_day = "Unknown"
                current_time = "Unknown"

                for row_idx, row in df.iterrows():
                    # Look for Day or Time markers in the row
                    row_text = " ".join([str(x).upper() for x in row.values])
                    
                    for day in days_of_week:
                        if day in row_text: current_day = day
                    
                    # Look for time patterns like 08:00 or 11:30
                    if ":" in row_text:
                        for cell in row:
                            if ":" in str(cell): current_time = str(cell)

                    for col_idx, cell_value in enumerate(row):
                        val = str(cell_value)
                        
                        # The "Magic Pattern": Class cells usually have newlines and a Room/Lab code
                        if "\n" in val and any(k in val.upper() for k in ["R00M", "LAB", "100-B", "99-B", "98-B"]):
                            parts = val.split("\n")
                            course = parts[0].strip()
                            teacher = parts[1].strip() if len(parts) > 1 else "TBA"
                            room = parts[2].strip() if len(parts) > 2 else "TBD"
                            
                            # Guess section from column header or filename
                            section = str(df.columns[col_idx])
                            if "Unnamed" in section or len(section) < 2:
                                section = file.split('Schedule')[0].strip()

                            final_data.append({
                                'Day': current_day,
                                'Time': current_time,
                                'Course': course,
                                'Teacher': teacher,
                                'Section': section,
                                'Room': room,
                                'Is_Lab': "LAB" in room.upper()
                            })
        except Exception as e:
            print(f"⚠️ Error in {file}: {e}")

    # Final Save
    clean_df = pd.DataFrame(final_data)
    # Remove junk
    clean_df = clean_df[~clean_df['Course'].str.contains('Revised|contact|date', case=False)]
    clean_df.to_csv('standardized_university_data.csv', index=False)
    print(f"\n✅ SUCCESS! I found {len(clean_df)} valid classes across all files.")

if __name__ == "__main__":
    scrape_everything()