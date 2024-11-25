# Genetic Variation Search tool

The Genetic Variation Search tool is a web based bioinformatics tool designed for users to search for genetic variations linked to a specific phenotype or a gene symbol. It connects to a mysql database to retrieve and show detailed information about the user search like: allele ID, mutation type, genomic locations and clinical significance.

**NOTE: The data used is of *Homo sapiens* specifcally GRCh38 assembly**
## Prerequisites

The following prerequisites must be met for python and the modules needed:
- **Python version**: Python 3.*
- `jinja2` to render template.
- `mysql-connector` to connect to the database.

 **to install the required modules**, run:
 ```bash
 pip install mysql-connector-python jinja2
```

- **MySQL** Server must be installed and running. 
The server must contain a database with the configured schema as entailed in the schema overview section.

- **Apache** Must be installed and configured to execute the python CGI script.
**NOTE: make sure that the mod_cgi module is enabled and that your Apache configuration points to the directory containing the CGI script to not run into errors.*

- **HTML template** must be placed in ./templates directory relative to the CGI script.

## Database Schema Overview

before beginning to populate the database, it is important to understand the schema structure. Below is an overview of the key tables used:

- **`genes`**: stores gene information.
  - `gene_id` (INT, PRI key, auto increment)
  - `gene_symbol` (varchar(80), unique)
  - `hgnc_id`(varchar(100))

- **`variants`**: contains data about genetic variants associated with genes.
  - `variant_id` (INT, primary key, auto_increment)
  - `allele_id` (INT, unique)
  - `gene_id` (INT, foreign key to `genes` table)
  - `type` (VARCHAR(100))
  - `chromosome` (VARCHAR(15))
  - `start` (INT)
  -  `stop` (INT)
  -  `cytogenetic` (VARCHAR(60))

- **`variant_references`**: contains references from external databases for the variants.
  - `variant_id` (INT, foreign key to `variants` table)
  - `variant_db` (VARCHAR(100))
  - `variant_id` (VARCHAR(100))
  
- **`phenotypes`**: storing the phenotype names connected to genetic variants.
  - `phenotype_id` (INT, PRI KEY, auto_increment)
  - `phenotype_name` (text)

- **`variant_phenotype`**: the table links variants to phenotype and include the clinical significance.
   - `variant_id` (INT, foreign key to `variants` table)
   - `phenotype_id` (INT, foreign key to `phenotypes` table)
   - `clinical_significance` (VARCHAR(255))

## Relationships
- The **`genes`** table is linked to **`variants`** table by `gene_id`
- The **`variant_rcv`** and **`variant_references`** tables are linked to **`variants`** table by `variant_id`
- The **`variant_phenotype`** is a bridge table between **`variants`** and **`phenotype`** table by `gene_id`
**Note**: please make sure that your database schema follows the previous structure before running `ppd.py` to avoid errors :-)

 ## Populating the database
 Before we set up the database, we must get the raw data from [Clinvar](https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz) 
 By:
 ```bash
 wget https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz
```

### 1. **make sure the previous prerequisites are met**
- Make sure the modules mentioned previously in the **Prerequisites** section are installed.
- Also make sure that MySQL server is running and configured with the previous mentioned tables.
### 2. **Run the python script**
- Modify the database connection details in the script to match your local configuration:
  ```python
  conn = mysql.connector.connect(user='your_username', password='your_password', host='your_host', database='your_database_name')
  ```
- Run the python script to populate the database:
  ```bash
  python3 ppd.py
  ```
## Directory structure
Below is the directory structure for the tool to work:
```bash
.
├── css
│   └── result.css
├── form_handle.html
├── gvs.cgi
├── js
│   ├── form_handle.js
│   └── results_display.js
└── templates
    └── results_display.html
```

## Usage Guide
once everything has been set up as instructed, please follow these steps to use it:
1. **Access the tool**:
   - Open a web browser and use the URL where the `form_handle.html` is hosted (e.g. `http://localhost/test04/form_handle.html`
2. **Performing a search**:
   - once the HTML loads, enter either a **gene symbol** or **phenotype** then from the option dropdown menu, choose one of the options given then submit the search.
3. **Viewing results**:
   - Results are shown in a table format for easy review where it includes all relevant details linked to the searched gene or phenotype.
  
## Troubleshooting
-  **Database connection errors**:
   - Double check your database credentials in `ppd.py` so that it matches your MySQL setup.
   - Make sure that your MySQL server is accessible.
- **CGI script errors**:
  - Make sure that Apache is configured correctly and that the `mod_cgi`  module is enabled
  - check that the CGI script has correctly executable permissions.
- **Missing data**:
  - Make sure that `variant_summary.txt` exists in the same directory as `ppd.py`.
  - Double check that the file has been unzipped and is not corrupted.




