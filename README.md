Smart Data Analyzer

A Python and Streamlit-based web application designed for interactive, no-code data analytics. This tool allows users to seamlessly upload datasets, perform data cleaning, run statistical analysis, and generate visualizations. It is optimized for deployment via Google Colab using a Cloudflare Tunnel for stable, password-free access.

Features

File Support: Upload CSV or Excel datasets.

Data Cleaning: Non-destructive handling of missing values and data quality issues.

Statistical Analysis: Instantly generate statistical summaries and metrics for your datasets.

Data Visualization: Create custom charts and graphs without writing any code.

Export: Download generated reports and cleaned data easily.

Tech Stack

Python

Streamlit

Pandas, NumPy

Matplotlib, Seaborn

Repository Structure

app.py - The main Streamlit application code.

requirements.txt - List of Python dependencies required to run the app.

cloudflare_setup.txt - The exact terminal commands needed to install Cloudflared, run Streamlit in the background, and expose the server on Google Colab.

How to Run on Google Colab

Because Google Colab runs on a virtual machine without a direct display, you must use a Cloudflare Tunnel to view the web interface. Follow these steps in order:

Open Google Colab and create a new notebook.

Cell 1 (Install Dependencies): Copy and paste the following command and run the cell:

!pip install streamlit pandas numpy matplotlib seaborn openpyxl


Cell 2 (Create the App File): Open app.py from this repository, copy the entire code, paste it into the second cell (ensure %%writefile app.py is at the very top line of the cell), and run it.

Cell 3 (Setup Cloudflared): Open cloudflare_setup.txt from this repository, copy the Cell 3 block to download and configure cloudflared, paste it into the third cell, and run it.

Cell 4 (Start Server & Tunnel): Copy the Cell 4 block from cloudflare_setup.txt, paste it into the fourth cell, and run it.

Open the App: Look at the Cloudflare server logs in the output of Cell 4 for a generated URL ending in .trycloudflare.com and click it to launch your web application.
