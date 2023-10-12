# azcs-skillset-functions
Collection of Azure Functions developed in Python to be added to an existing Cognitive Search Skillset

Each is a code block of a sample Azure Function that could be added to a skillset of an Azure Cognitive Search index.

Endpoints and Service keys are defined as configurations witin the Azure Function definition, hence the 'os.environ' calls.

Each Python source file has a corresponding 'local.settings.json' and 'requirements.txt' file for deploying the function via Visual Studio Code.

Each file will need to be renamed to be useful - for example :

* detect-metatag-strings.py
* metatag-requirements.txt : rename to 'requirements.txt'
* metatag.local.settings.json : rename to 'local.settings.json'

<b>PLEASE NOTE :</b> Two of the sample functions contain a JSON block for words and phrases that are categorized, as well as a URL.

<b>These are NOT official in any shape or form. They are completely fictitious, to the best of my knowledge.</b>
