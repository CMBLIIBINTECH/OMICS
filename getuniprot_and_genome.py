#download and sep all uniprot proteomes and their associated genomes
import os
import subprocess
import shlex
import urllib2,urllib
from Bio import Entrez

outdir = './OMIC_DATA'
proteome_refs= 'proteomes-all.tab'
contact = "dmoi@iibintech.com.ar"

get_prots = True
get_genes = True
def checkdir(dir):
	if not os.path.exists(dir):
		os.makedirs(dir)

with open(proteome_refs) as refs:
	proteomes = {}
	i = 0
	for line in refs:
		if i == 0:
			keys = []
			words = line.split('	')
			for word in words:
				keys.append(word)
		if i > 0 :
			words = line.split('	')
			proteomes[i] = {}
			ikeys = iter(keys)
			for word in words:
				proteomes[i][next(ikeys)] = word 
		i+=1
	else:
		print 'done'	


for i in proteomes.keys():
	print proteomes[i]['Organism']
	orgout = outdir +'/' +proteomes[i]['Organism ID'] + '/'
	checkdir(orgout)
	if get_prots:
		print ' getting proteome for ' + proteomes[i]['Organism']
		proteomefile = orgout + proteomes[i]['Organism ID']+'_proteome.gz'
		url = 'http://www.uniprot.org/uniprot/?query=proteome:'+proteomes[i]['Proteome ID'] +'&format=fasta&compress=yes'
		urllib.urlretrieve (url, proteomefile)
		args = 'gzip -d ' + proteomefile  
		args = shlex.split(args)
		subprocess.call( args)
		args = 'rm ' + proteomefile
		args = shlex.split(args)
		#subprocess.call( args) 

	if get_genes:
		Entrez.email = contact
		Ids = Entrez.read(Entrez.esearch(db="genome", term= 'txid'+proteomes[i]['Organism ID'] +  '[Organism:noexp]', retmode='xml'))
		if len(Ids['IdList'])>0:
			record = Entrez.read(Entrez.efetch(db="genome", id= Ids['IdList'][0] , rettype = 'docsum',retmode='xml'))
			Ids = Entrez.read(Entrez.esearch(db="assembly", term= record[0]['Assembly_Accession'] , retmode='xml'))
			url = 'http://www.ncbi.nlm.nih.gov/nuccore?LinkName=assembly_nuccore_refseq&from_uid='+Ids['IdList'][0]
			try:
				Ids = Entrez.read(Entrez.elink(db="nuccore", dbfrom = 'assembly', from_uid= Ids['IdList'][0]))
				#select the smallest set of nuccore refs from genome assemby ref
				if Ids: 
					numlinks=0
					assembly_refs = {}
					for entry in Ids[0]['LinkSetDb']:
						links = len(entry['Link'])
						if numlinks > links or numlinks == 0:
							numlinks = links
							assembly_refs = entry
			except:
				print 'cant find assembly'
			print 'getting genome of ' + proteomes[i]['Organism']
			for entry in assembly_refs['Link']:
				docfile = Entrez.read(Entrez.efetch(db="nuccore", id= entry['Id'] , retmode='xml' , rettype = 'docsum'))
				sequences = Entrez.efetch(db="nuccore", id= entry['Id'] , retmode='text' , rettype = 'fasta')
				genomefile =orgout+ proteomes[i]['Organism ID']+'_genome.fasta'
				with open( genomefile, 'a') as outfile:
					for line in sequences:
							outfile.write(line)