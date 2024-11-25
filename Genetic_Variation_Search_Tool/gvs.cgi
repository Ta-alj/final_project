#!/usr/local/bin/python3
import cgi
import mysql.connector
import jinja2

result_lm = 50
templateloader = jinja2.FileSystemLoader( searchpath="./templates")
env = jinja2.Environment(loader=templateloader)
template = env.get_template("results_display.html")

print("content-type: text/html")
print()

form = cgi.FieldStorage()
search_term = form.getvalue('search_term')
search_type = form.getvalue('search_type')
cur_page = int(form.getvalue('page', 1))

conn = mysql.connector.connect(user='your_username', password='your_password', host='your_host', database='your_database_name')
cursor = conn.cursor()

if search_type == 'gene':
    count_query = """select count(distinct v.variant_id)
    from genes g 
    left outer join variants v on g.gene_id = v.gene_id
    where g.gene_symbol like %s;"""
    user_query = """select g.gene_symbol as gene, g.hgnc_id as HGNC_ID, v.allele_id, v.type, v.start, v.stop,
    v.cytogenetic as cytogenetic_location, group_concat(distinct vr.reference_db, ':', vr.reference_id order by vr.reference_db SEPARATOR '; ') as reference_info,
    group_concat(distinct p.phenotype_name order by p.phenotype_name SEPARATOR '; ') as phenotype_names,
    group_concat(distinct vp.clinical_significance order by vp.clinical_significance SEPARATOR '; ') as clinical_significances
    from genes g
    left outer join variants v ON g.gene_id = v.gene_id left outer join variant_references vr on v.variant_id = vr.variant_id
    left outer join variant_phenotype vp on v.variant_id = vp.variant_id
    left outer join phenotypes p on vp.phenotype_id = p.phenotype_id
    where g.gene_symbol like %s
    group by g.gene_symbol, v.variant_id order by g.gene_symbol limit %s offset %s;"""
    search_value = f"{search_term}%"
elif search_type == "phenotype":
    count_query = """select count(distinct v.variant_id)
    from phenotypes p 
    left outer join variant_phenotype vp on p.phenotype_id = vp.phenotype_id
    left outer join variants v on vp.variant_id = v.variant_id
    where p.phenotype_name like %s;"""
    user_query = """
select g.gene_symbol as gene, g.hgnc_id as HGNC_ID, v.allele_id, v.type, v.start, v.stop,
        v.cytogenetic as cytogenetic_location, group_concat(distinct vr.reference_db, ':', vr.reference_id order by vr.reference_db SEPARATOR '; ') as reference_info,
        group_concat(distinct p.phenotype_name order by p.phenotype_name SEPARATOR '; ') as phenotype_names,
        group_concat(distinct vp.clinical_significance order by vp.clinical_significance SEPARATOR '; ') as clinical_significances
        from genes g
        left outer join variants v ON g.gene_id = v.gene_id left outer join variant_references vr on v.variant_id = vr.variant_id
        left outer join variant_phenotype vp on v.variant_id = vp.variant_id
        left outer join phenotypes p on vp.phenotype_id = p.phenotype_id
        where p.phenotype_name like %s
        group by g.gene_symbol, v.variant_id order by g.gene_symbol limit %s offset %s;
    """
    search_value = f"{search_term}%"
else:
    print("<h1>Error: Please choose a valid search type</h1>")
    cursor.close()
    conn.close()
    exit()

cursor.execute(count_query, (search_value,))
total_records = cursor.fetchone()[0]
if total_records % result_lm != 0:
    total_pages = (total_records // result_lm) + 1
else:
    total_pages = total_records // result_lm

cursor.execute(user_query, (search_value, result_lm, (cur_page - 1) * result_lm))
results = cursor.fetchall()

page_output = template.render(results=results, query=search_term, search_type=search_type, cur_page=cur_page,  total_pages = total_pages)
print(page_output)

cursor.close()
conn.close()
