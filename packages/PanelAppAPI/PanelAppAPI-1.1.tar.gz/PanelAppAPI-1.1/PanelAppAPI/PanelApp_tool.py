import requests
import json, re, argparse, os
from datetime import datetime
import pandas as pd

PANELAPP_URL = "https://panelapp.genomicsengland.co.uk/api/v1"

#Interface to PanelApp API. Allow extraction of genes using panel IDs or disease terms
class PanelApp():
    def __init__(self, url=PANELAPP_URL):
        self._url = url
        panels_list = list()
        uri = self._url + "/panels"
        while ( uri is not None):
            print(uri)
            get_request = requests.get(uri)
            if get_request.status_code != 200: raise Exception("Unable to get panels from", uri) 
            ppage = get_request.json()
            panels_list = panels_list + ppage['results']
            uri=ppage["next"]
        self._panels = pd.DataFrame.from_dict(panels_list)
        self._panels['n_genes'] = [x['number_of_genes'] for x in list(self._panels['stats'])]
        self._panels = self._panels[['id','name','disease_group','disease_sub_group','version','version_created','n_genes','relevant_disorders']]
        self._panels.set_index('id', inplace=True)
        now = datetime.now()
        self.time = now.strftime("%Y{sep}%m{sep}%d".format(sep=""))

    def listPanels(self, panel_id=False, name=False, disease=False):
        panels = []
        
        if not name and not disease and not panel_id:
            name='.*'
        
        if disease:
            r = re.compile(disease, re.IGNORECASE)
            mask = []
            for line in list(self._panels.relevant_disorders):
                mask.append(any(r.search(x) for x in line))
            selected_panels_disease = self._panels[mask]
            panels.append(selected_panels_disease)
            
        if name:
            selected_panels_name = self._panels[self._panels.name.str.contains(name,case=False,regex=True)]
            panels.append(selected_panels_name)
            
        if panel_id:
            selected_panels_id = pd.DataFrame(self._panels.loc[panel_id,]).transpose()
            panels.append(selected_panels_id)
        
        return pd.concat(panels)
              
    def getPanelId(self, name=False, disease=False):
        selected_panels = self.listPanels(name=name, disease=disease)
        return list(selected_panels.index)
    
    def getGenes(self, pid=False, name=False, disease=False, level=3, out_format="df", build="GRCh38"):
        #If all pid, name and disease are False, will download for all panels
        genes = pd.DataFrame(columns = ['entity_name','confidence_level','panel_name','penetrance','mode_of_inheritance','GRCh37','GRCh38'])
        panels = self.listPanels(pid,name,disease)
        ids = list(panels.index)
        for panel_id in ids:
            get_request = requests.get(self._url + "/panels/" + str(panel_id))
            if get_request.status_code != 200: 
                print("Unable to get genes for panel ", panel_id)
                continue
            
            if len(get_request.json()['genes']) == 0:
                continue
            else:
                panel_genes = pd.DataFrame.from_dict(get_request.json()['genes'])
                GRCh37_coords = list()
                GRCh38_coords = list()
                for x in panel_genes['gene_data']:
                    try:
                        GRCh37_coords.append(x['ensembl_genes']['GRch37']['82']['location'])
                    except:
                        GRCh37_coords.append("0:0-0")
                    try:
                        GRCh38_coords.append(x['ensembl_genes']['GRch38']['90']['location'])
                    except:
                        GRCh38_coords.append("0:0-0")
                panel_genes['GRCh37'] = GRCh37_coords
                panel_genes['GRCh38'] = GRCh38_coords
                panel_genes['panel_name'] = panels.name[panel_id]
                panel_genes['confidence_level'] = pd.to_numeric(panel_genes['confidence_level'])
                panel_genes = panel_genes[panel_genes.confidence_level >= level]
                panel_genes = panel_genes[['entity_name','confidence_level','panel_name','penetrance','mode_of_inheritance','GRCh37','GRCh38']]
                genes = pd.concat([genes, panel_genes])
            
                if out_format == "bed":
                    chrs_order = [str(x) for x in list(range(0,23)) + ['X','Y','M']]
                    coordinates = genes[build].str.extractall(r'([0-9XYM]+):(\d+)-(\d+)')
                    genes['chrom'] = pd.Categorical(coordinates[0].values, chrs_order)
                    genes['start'] = pd.to_numeric(coordinates[1].values)
                    genes['stop'] = pd.to_numeric(coordinates[2].values)
                    genes = genes[['chrom', 'start', 'stop','entity_name','panel_name']]
                    genes.sort_values(by=['chrom','start'], inplace=True)
            
                if out_format == "detailed_bed":
                    chrs_order = [str(x) for x in list(range(0,23)) + ['X','Y','M','MT']]
                    coordinates = genes[build].str.extractall(r'([0-9XYMT]+):(\d+)-(\d+)')
                    genes['chrom'] = pd.Categorical(coordinates[0].values, chrs_order)
                    genes['start'] = pd.to_numeric(coordinates[1].values)
                    genes['stop'] = pd.to_numeric(coordinates[2].values)
                    genes = genes[['chrom', 'start', 'stop','entity_name','confidence_level','penetrance','mode_of_inheritance']]
                    genes.sort_values(by=['chrom','start'], inplace=True)
        
        if len(genes.index) > 0:
            return True, genes
        else:
            return False, genes
    
    def dumpPanels(self, output_dir, panels="all", level=3, build="GRCh38"):
        if panels == "all": panels = list(self._panels.index)
        index_file = output_dir+"/Index_table_"+self.time+".tsv"
        index_df = self._panels.loc[panels]
        index_df['n_green'] = 0
        n_written_panels = 0
        for panel_id in panels:
            n_written_panels += 1
            #print("Saving panel ", panel_id)
            genes_file = output_dir+"/"+build+"_Panel_"+str(panel_id)+".bed"
            success, genes = self.getGenes(pid = panel_id, level=0, build=build, out_format="detailed_bed")
            if success:
                try:
                    n_green = int(genes.groupby('confidence_level').count().loc[3,'entity_name'])
                except:
                    n_green = 0
                genes = genes[genes.confidence_level >= level]
                header = list(genes.columns)
                header[0] = "#" + header[0]
                genes.to_csv(genes_file,sep="\t",index=False,header=header)
                index_df.loc[panel_id,'n_green'] = n_green
        index_df = index_df[['name', 'disease_group', 'disease_sub_group', 'version', 'version_created', 'n_genes', 'n_green', 'relevant_disorders']]
        index_df.sort_values(by=['name'], inplace=True)
        index_df.to_csv(index_file, sep="\t")
        return(n_written_panels)

def now(sep=""):
    now = datetime.now()
    current_time = now.strftime("%Y{sep}%m{sep}%d".format(sep=sep))
    return current_time

#Main function is to download all panels to a folder
#Without arguments will download green and amber genes for all GRCh38 panels to panelapp_[currentdate]
#Each panel is dumped in a file named by panel index. A master table describing each panel is also saved
def dumpPanels():

    parser = argparse.ArgumentParser(description='Dump all genes in PanelApp panels to bed like tables')
    parser.add_argument("-w", "--url", help="panelApp url", action="store", required=False, default=PANELAPP_URL)
    parser.add_argument("-o", "--out", help="Output folder", action="store", required=False, default="panelapp_" + now())
    parser.add_argument("-b", "--build", help="Genome build", action="store", choices=["GRCh37", "GRCh38"], required=False, default='GRCh38')
    parser.add_argument("-l", "--minlevel", help="Min level of confidence", action="store", choices=[1,2,3], required=False, default=2)
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    panelapp = PanelApp(args.url)

    n_panels = panelapp.dumpPanels(args.out, build=args.build, level=args.minlevel)

    print(n_panels, "saved")
    print("All panels saved to", args.out)
