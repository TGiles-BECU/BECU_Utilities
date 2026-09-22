from pathlib import Path
import pandas as pd
from premailer import transform
from . import purge90

def run(idx, og_body):
    Path(idx)
    sel_date = idx.stem.split("_")[1]
    file_name_pattern = "Funded_Loans_Current_Day-" + sel_date
    
    report_folder = Path("//fs01/Company/Keystone Reports/Technology")
    input_csv = None
    
    for file in report_folder.iterdir():
        if file.is_file():
            if file_name_pattern.lower() in file.name.lower():
                print(f"Targeted file found: {file.name}")
                input_csv = file
                break
                
    if not input_csv:
        raise FileNotFoundError(f"Error: No .csv dated '{sel_date}' in '{report_folder}'")
        
    df = pd.read_csv(input_csv)

    df = df[~df["Fund Date"].astype(str).str.contains("total", case=False, na=False)]

    df["Account Number"] = df["Account Number"].astype(str).str.lstrip("0")

    df["Loan ID"] = df["Loan ID"].astype(str).str.split(".").str[0]

    df["Credit Score"] = pd.to_numeric(df["Credit Score"], errors="coerce").astype("Int64")

    tin_clean = df["Member TIN"].astype(str).str.split(".").str[0]
    tin_clean = tin_clean.str.zfill(9)

    df["Member TIN"] = "***-**-*" + tin_clean.str[-3:]
    
    strike_pairs = set()
    with open(idx, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split("|")
            if len(parts) >= 2:
                acc = parts[0].strip()
                loan = parts[1].strip()
                strike_pairs.add((acc, loan))
    
    def apply_row_styles(row):
        # Determine alternating background color based on row index
        if row.name % 2 == 0:
            bg_color = "background-color: #F0F4F8;"  # Light ice blue
        else:
            bg_color = "background-color: #F8FAFC;"  # Very light off-white blue
            
        return [bg_color] * len(row)
    
    def strikethrough_account(row):
        acc = str(row["Account Number"]).split(".")[0].strip()
        loan = str(row["Loan ID"]).split(".")[0].strip()
        
        if (acc, loan) in strike_pairs:
            return ["text-decoration: line-through; color: #888888;"] * len(row)
        
        # This is where we could draw attention to loans that were NOT imported as well.
        return [""] * len(row)
        
    def mask_account(val):
        val_str = str(val).split(".")[0].strip()
        return "*******" + val_str[-3:] if len(val_str) >= 3 else val_str

    styled_df = (
        df.style
        .apply(apply_row_styles, axis=1)
        .apply(strikethrough_account, axis=1)
        .format({"Account Number": mask_account})  # Alters display ONLY, leaves raw data intact
        .hide(axis="index")
        .set_properties(**{'text-align': 'left', 'padding': '8px'})
        .set_table_styles([
            # 2. Header styling: Dark blue background, white left-aligned text
            {
                'selector': 'th',
                'props': [
                    ('background-color', '#1B365D'),
                    ('color', '#FFFFFF'),
                    ('text-align', 'left'),
                    ('padding', '8px'),
                    ('font-weight', 'bold')
                ]
            }
        ])
    )
        
    html_table = styled_df.to_html(
        index=False,
        classes="sytled-table",
        na_rep="-",
        border=0,
        table_attributes='style="border-collapse: collapse; width: 100%; font-family: Arial, sans-serif;"'
    )
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .styled-table {{
            border-collapse: collapse;
            width: 100%;
            margin: 25px 0;
            font-size: 0.9em;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }}
        .styled-table thead tr {{
            background-color: #009879;
            color: #ffffff;
            text-align: left;
        }}
        .styled-table th, .styled-table td {{
            padding: 12px 15px;
            border: 1px solid #dddddd;
        }}
        .styled-table tbody tr:nth-of-type(even) {{
            background-color: #f3f3f3;
        }}
    </style>
</head>
<body>
    {og_body.replace('\n', '<br>')}
    <h2>{sel_date} Funded Loans:</h2>
    {html_table}
</body>
</html>
"""
    
    # Clean Up
    purge90.move(input_csv, "Account Docs")
    
    return transform(html_content)