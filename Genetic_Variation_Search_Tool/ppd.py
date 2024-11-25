#!/usr/local/bin/python3
import mysql.connector
import time

conn = mysql.connector.connect(user='your_username', password='your_password', host='your_host', database='your_database_name')
cursor = conn.cursor()
file = "variant_summary.txt"
processed_rows = 0
start_time = time.time()
print("Starting to parse the file..")
with open(file, "r") as f:
    for line in f:
        if line.startswith("#"):
            continue

        columns = line.split("\t")
        allele_id = columns[0]
        variant_type = columns[1]
        gene_symbol = columns[4]
        hgnc_id = columns[5]
        chromosome = columns[18]
        start = columns[19]
        stop = columns[20]
        phenotype_list = columns[13].split("|")
        assembly = columns[16]
        clinical_significance = columns[6].lower().strip()
        references_db = columns[12].split("|")
        cytogenetic_location = columns[23]

        #beginning of the cursed nested if statement, this has been hell. good luck!
        if gene_symbol == "-":
            continue

        # this to filter out any irrelevant records and only relevant records
        if assembly == "GRCh38" and clinical_significance != "uncertain significance":
            if "covers" in gene_symbol.lower():
                continue

            # this chunk is cursed but will handle gene symbols aggregates.
            if "subset of" in gene_symbol:
                subset_gene = gene_symbol.split("subset of", 1)[1].strip()
                main_gene = subset_gene.split(":", 1)[1].split(":")[0].strip()
            else:
                main_gene = gene_symbol.split(";")[0].strip()
            gene_symbol = main_gene
        else:
            continue

        #inserting genes if it doesnt exist
        cursor.execute("select gene_id from genes where gene_symbol = %s", (gene_symbol,))
        gene_result = cursor.fetchone()
        if gene_result:
            gene_id = gene_result[0]
        else:
            cursor.execute("insert into genes (gene_symbol, hgnc_id) values (%s, %s)", (gene_symbol, hgnc_id))
            gene_id = cursor.lastrowid

        #inserting variants if it doesnt exist
        cursor.execute("select variant_id from variants where allele_id = %s", (allele_id,))
        variant_result = cursor.fetchone()
        if variant_result:
            variant_id = variant_result[0]
        else:
            cursor.execute("insert into variants (allele_id, gene_id, type, chromosome, start, stop, cytogenetic) values (%s, %s, %s, %s, %s, %s, %s)",(allele_id, gene_id, variant_type, chromosome, start, stop, cytogenetic_location))
            variant_id = cursor.lastrowid

        #inserting dbs links  into variant_references
        for ref_group in references_db:
            for ref in ref_group.split(","):
                if ":" in ref:
                    db_name = ref.split(":", 1)[0]
                    ref_id = ref.split(":", 1)[1].split(",")[0]
                    cursor.execute("select * from variant_references where variant_id = %s and reference_db = %s and reference_id = %s ", (variant_id, db_name, ref_id,))
                    if not cursor.fetchone():
                        cursor.execute("insert into variant_references (variant_id,reference_db, reference_id) values(%s, %s, %s)", (variant_id, db_name, ref_id,))

        #chunk for processing phenotypes and inserting them.
        not_good_terms = ["conditions", 'see case', 'see cases', 'not provided']
        for phenotype_name in phenotype_list:
            if any(term in phenotype_name.lower() for term in not_good_terms):
                continue

            cursor.execute("select phenotype_id from phenotypes where phenotype_name = %s", (phenotype_name,))
            phenotype_result = cursor.fetchone()
            if phenotype_result:
                phenotype_id = phenotype_result[0]
            else:
                cursor.execute("insert into phenotypes (phenotype_name) values (%s)", (phenotype_name,))
                phenotype_id = cursor.lastrowid

            cursor.execute("insert into variant_phenotype (variant_id, phenotype_id, clinical_significance) values (%s, %s, %s)", (variant_id, phenotype_id, clinical_significance))

        processed_rows += 1
        if processed_rows % 100000 == 0:
            elapsed_time = time.time() - start_time
            print(f"Processed {processed_rows} rows in {elapsed_time} seconds")

conn.commit()
total_time = time.time() - start_time
print(f"Total time to process all entries: {total_time / 3600:.2f} hours")
cursor.close()
conn.close()
