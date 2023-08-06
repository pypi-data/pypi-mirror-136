# PanelApp tools

This containts a simple class to interact with the PanelApp API. See the (PanelApp website)[https://panelapp.genomicsengland.co.uk/]

The main class is `PanelApp`.


This also expose a cli command `panelapp_dump` that can be used to download PanelApp panels to tables. By default, it will download GREEN and AMBER genes for all panels in GRCh38 version into `panelapp_[currentdate]` folder.

You can user arguments to change genome build, output folder and gene confidence level (see `--help`)

Following methods are available in the `PanelApp` class

- `listPanels(self, panel_id=False, name=False, disease=False)` :
Return pandas dataframe of panels based on the search criteria. When no criteria used returns for all panels. Search criteria work as OR.
        
- `getPanelId(self, name='.*', disease='.*')`
Return list of panels ids according to the search criteria.  Search criteria work as OR.

- `getGenes(self, pid=False, name=False, disease=False, level=3, out_format="df", build="GRCh38")`
Return True/False (indicating if any genes found) and a pandas dataframe for the genes of interest. First search for relevant panels using the `pid`, `name` and `disease`, then for the resulting panels get genes informations for genes with level above the value set by `level` option (level 3 = GREEN genes, 2 = AMBER, 1 = RED). 
You can ask for `GRCh38` or `GRCh37` coordinates and the returned dataframe can be structure as a BED file using `out_format="bed"`

- `dumpPanels(self, output_dir, panels="all", level=3, build="GRCh38")`
Save panels to disk as tables of genes named by panel id and also save a index table describing panels for each panel id.
You can pass a list of panel ids to `panels` or use all to save all panels. 
You can set the minimum level of confidence for saved genes using `level` and the genome build for coordinates using `build`.
