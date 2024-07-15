# Spell checker for Qgis Print Layouts

## Installation 

Before you can use this plugin you **must** install the `pyspellchecker` using your preferred python package 
manager. I used `pip install pyspellchecker`.

## Usage 

When you attempt to output a print layout all the **text** elements of the layout will be scanned for 
misspelled words and a suggested fix will be offered. If you need to edit any words then select `cancel` and 
fix the error if you don't care then press `ok` and proceed.

### Custom Dictionary

You can add a file of words that you don't want to be considered as misspellings. The default location is 
`$HOME/.local/share/QGIS/QGIS3/profiles/default/spelling.txt`. It is a simple file of words one to a line. If 
you would like to use a different file then this can be set in the plugin GUI (`plugins->Spell Check`)
