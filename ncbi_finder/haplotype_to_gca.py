import sys
import csv
import requests
from mysql.connector import (
    cursor,
    connect
)

# GCA/042/077/495
# GCA_042077495.1_NA19036_hap1_hprc_f2
# GCA_042077495.1_NA19036_hap1_hprc_f2


NCBI_FTP_PATH = "https://ftp.ncbi.nlm.nih.gov/genomes/all/{}/{}/{}_assembly_report.txt"

GET_ASSEMBLY_SQL = """
select distinct(a.accession), a.name, a.assembly_uuid,
da.value as assembly_level, g.genome_uuid, o.biosample_id
from assembly a
left join genome g on (g.assembly_id = a.assembly_id)
left join genome_dataset gd on (gd.genome_id = g.genome_id )
left join dataset_attribute da on (da.dataset_id = gd.dataset_id )
left join organism o on (o.organism_id = g.organism_id )
where a.name like "{}%"
and da.attribute_id = 9"""


def get_connection():
    host = "mysql-ens-production-1.ebi.ac.uk"
    port = 4721
    user = "ensro"
    database = "ensembl_genome_metadata"
    try:
        mydb = connect(
            host=host,
            port=port,
            user=user,
            password=None,
            database=database,
        )
    except Exception:
        print("Failed to connect to database")
        sys.exit(-1)

    return mydb


def get_haplotypes_from_file(file) -> list[str]:
    with open(file) as file_str:
        return file_str.read().split('\n')


def chunk_gca(gca: str) -> list[str]:
    chunk = 3
    if "." in gca:
        gca = gca.split(".")[0]
    if "_" in gca:
        gca = gca.replace("_", "")
    return [gca[i:i+chunk] for i in range(0, len(gca), chunk)]


def ncbi_url(gca: str, haplotype: str) -> str:
    chunked_gca = "/".join(chunk_gca(gca))
    gca_plus_name = f"{gca}_{haplotype}"

    return NCBI_FTP_PATH.format(
        chunked_gca,
        gca_plus_name,
        gca_plus_name
    )


def is_haplotype(url: str) -> bool:
    # make call to ncbi
    results = requests.get(url)
    if results.ok:
        # parse report
        lines = results.text.splitlines(False)
        print(lines[9])
        if "Assembly type" in lines[9]:
            tar = lines[9].lower()
            is_diployed = "2" in tar or "diploid" in tar
            return not is_diployed
    # return response
    print("defaulting")
    return True


def get_gcas(haplotypes):
    my_db = get_connection()
    my_cursor = my_db.cursor()
    results = []
    columns = [
        "accession",
        "name",
        "assembly_uuid",
        "assembly_level",
        "genome_uuid",
        "biosample_id",
        "ncbi",
        "is_haplo"
        ]
    not_from_db = ["ncbi","is_haplo"]
    output_columns = ["haplotype"]
    output_columns.extend(columns)
    for haplo in haplotypes:
        search_haplo = haplo
        if "." in search_haplo:
            search_haplo = search_haplo.split('.')[0]
        print(search_haplo)

        sql = GET_ASSEMBLY_SQL.format(search_haplo)
        my_cursor.execute(sql)
        found = False
        for row in my_cursor.fetchall():
            found = True
            dict_row = {
                   output_columns[0]: haplo
            }

            dict_row.update(
                {columns[x]: row[x] for x in range(0, len(columns))
                    if columns[x] not in not_from_db}
                )
            dict_row["ncbi"] = ncbi_url(row[0], row[1])

            is_haplo = is_haplotype(dict_row["ncbi"])
            dict_row["is_haplo"] = "1" if is_haplo else "2"

            if (is_haplo == (".1" in haplo)):
                results.append(dict_row)
        if not found:
            missing_dict = {
                output_columns[0]: haplo
            }
            missing_dict.update({col: "-" for col in columns})
            results.append(missing_dict)
    with open("report.csv", "w") as csv_stream:
        writer = csv.DictWriter(csv_stream, fieldnames=output_columns)
        writer.writeheader()
        for row in results:
            writer.writerow(row)


if __name__ == "__main__":
    haplotypes = get_haplotypes_from_file(sys.argv[1])
    get_gcas(haplotypes)
