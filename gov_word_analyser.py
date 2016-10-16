import psycopg2
import pandas as pd

conn = psycopg2.connect("dbname=postgres user=postgres")
cur = conn.cursor()

query_interventions = """\
CREATE TABLE interventions AS \
SELECT to_char(speechdate,'YYYY') as year, speakerparty, count(*) as interventions \
FROM dilipadsite_basehansard \
WHERE TRIM(speakerparty) <> '' \
GROUP BY year, speakerparty \
ORDER BY year, interventions desc;\
"""

query_themes = """\
CREATE TABLE {} AS \
SELECT to_char(speechdate,'YYYY') as year, speakerparty, count(*) as {} \
FROM dilipadsite_basehansard \
WHERE TRIM(speakerparty) <> '' AND lower(speechtext) LIKE '%{}%' \
GROUP BY year, speakerparty \
ORDER BY year, {} desc;\
"""

query_exist = """\
SELECT EXISTS(SELECT * \
FROM information_schema.tables \
WHERE table_name =%s);\
"""

'''
Using the LIPAD dilipadsite_basehansard postgresql database, this programs
extracts key words said by parties and count the total number of time these
words were part of a speech.
'''
def main():
	themes = ["environment", "climate change", "coal", "nuclear", "gas", "oil",
			  "petrol", "solar power", "wind power"]
	generate_tables(themes)
	table = join_tables(themes)
	output(table,themes)
	output_transform()
	cleanup(themes)
	print "Run finished succesfully!"

	
'''
generate_tables uses a list of key words and look for the number of time these
words were part of a speech. The speaches are then counted by party and a table
following this structure is commited to the database:

name = <word>

year | party | <word>

It also returns a similar table that count the total number of interventions
made by a specific party every years. This table follows the following structure.

name = interventions

year | party | interventions
'''
def generate_tables(themes):
	print "Generating SQL tables..."
	cur.execute(query_exist, ("interventions",))
	if not cur.fetchone()[0]:
		cur.execute(query_interventions)
		conn.commit()
	else:
		cur.execute("DROP TABLE interventions;")
		conn.commit()
		cur.execute(query_interventions)
		conn.commit()

	for theme in themes:
		word_theme = "_".join(theme.split(" "))
		query_thematic = query_themes.format(word_theme,word_theme,theme,word_theme)
		cur.execute(query_exist, (word_theme,))
		if not cur.fetchone()[0]:
			cur.execute(query_thematic)
			conn.commit()
		else:
			cur.execute("DROP TABLE {}".format(word_theme))
			conn.commit()
			cur.execute(query_thematic)
			conn.commit()

'''
Generated tables are then joined using the year and party as primary keys.
join_tables will then fetchall() the joined table and return it. Using left 
outer join insures that all the parties that spoke during a year have an output.
The resulting table is as follow:

Name = None -> It is returned has a fetchall() list of tuple

year | party | interventions | <word1> | <word2> | <word n>
'''			
def join_tables(themes):
	print "Joining SQL tables..."
	final_themes = []
	for theme in themes:
		name = "_".join(theme.split(" "))
		db_name = name+"."+name
		final_themes.append(db_name)
		
	final_columns = ", ".join(final_themes)

	join_query = ("SELECT i.year, i.speakerparty, i.interventions, " + final_columns +
			" FROM interventions i")
			
	for theme in themes:
		name = "_".join(theme.split(" "))
		join_query += " LEFT OUTER JOIN {} on ({}.year = i.year AND {}.speakerparty = i.speakerparty)".format(name,name,name)
			
	cur.execute(join_query)
	return cur.fetchall()

'''
output() will create a file that takes a list of tuple generated by join_tables
and write a csv file named "output.csv" and delimited by ";".
'''
def output(table,themes):
	print "Creating the wide format csv output..."
	with open("output.csv", "w") as f:
		f.write("year,party,intervention," + ",".join(themes) + "\n")
		for line in table:
			f.write(','.join(map(str, line)) + "\n")
			
			
'''
output_transform() takes a file following the output format with every first 
column being the year, second: the party,third: number of interventions. The 
following columns represents the count for every extracted words. This wide
format is then transformed to a long format.
'''

def output_transform():
	print "Creating the long format csv output..."
	df = pd.read_csv("output.csv")
	df_transform = pd.melt(df, id_vars = ["year", "party", "intervention"], var_name = "type", value_name = "count")	
	df_transform["count"].replace("None", 0, inplace=True)
	df_transform.to_csv("output_transformed.csv", index = False)

'''
cleanup() finally cleans up all the tables that were generated in the 
generate_tables function. This will restore the original lipad postgresql
database.
'''
def cleanup(themes):
	print "Cleaning the SQL databases from the created tables..."
	cur.execute("DROP TABLE interventions")
	conn.commit()
	for theme in themes:
		name = "_".join(theme.split(" "))
		query_delete = "DROP TABLE {}".format(name)
		cur.execute(query_delete)
		conn.commit()
		
if __name__ == "__main__":
	main()

