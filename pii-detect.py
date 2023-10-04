import logging, json, os, requests

import azure.functions as func

def main( req: func.HttpRequest ) -> func.HttpResponse:

    logging.info( 'Python HTTP trigger function processed a request.' )

    try:

        body = json.dumps( req.get_json() )
    
    except ValueError :
        
        return func.HttpResponse(
            
            "Invalid body",
            status_code = 400
        
        )
    
    if body :

        # logging.info( "Pre-Check : " + str( body ) )

        result = fnBuildResponse( body )

        verifyResults = json.loads( result)

        resultValues = verifyResults[ "values" ]

        for value in resultValues :

            logging.info( "Discovered RecordId : " + str( value[ "recordId" ] ) )

            resultsData = value[ "data" ]

            textRecord = resultsData[ "redactedText" ]

            verifyText = textRecord[ : 25 ]

            logging.info( "Redacted Text Preview: " + str( verifyText ) )
        
        return func.HttpResponse( result, mimetype = "application/json" )
    
    else :
        
        return func.HttpResponse(
            
            "Invalid body",            
            status_code = 400
        
        )
    
def fnBuildResponse( json_data ) :

    maxSize = 5000

    jsonInput = json.loads( json_data )

    values = jsonInput[ 'values' ]
    
    # Prepare the Output before the loop
    results = {}
    results[ "values" ] = []

    for value in values :

        processedList = []
        returnBlock = ""

        # recordId = value[ "recordId" ]

        try :

            recordId = value[ "recordId" ]

            assert( "data" in value ), "'data' field is required."

            data = value[ "data" ]

            assert( "merged_content" in data ), "'merged_content' field is required in 'data' object."

            inputText = data[ "merged_content" ]

        except AssertionError as err :

            return(
                {
                    "recordID" : recordId ,
                    "data" : { "redactedText" : "Error : " + str( err ) }
                }
            )

        firstPass = inputText.replace( " \n", " " )

        cleanText = firstPass.replace( "\n", " " )

        # logging.info( "Clean Text : " + str( cleanText ) )

        if len( cleanText ) > maxSize :

            blockList = []

            blockList = [ cleanText[ i : i + 5000 ] for i in range( 0, len( cleanText ), 5000 ) ]

        elif len( cleanText ) > 2 and len( cleanText ) <= maxSize :

            blockList = []

            blockList.append( cleanText )

        else :

            logging.info( "Cleaned input is empty...")

            blockList = []

        if len( blockList ) > 0 :

            for block in blockList :

                processedBlock = fnDetectPII( block )

                processedList.append( processedBlock )

                for pBlock in processedList :

                    returnBlock += pBlock

        else :

            logging.info( "No text to run detection for value with recordID of " + str( recordId ) )

            returnBlock = " "

        outputJson =  {
            "recordId" : recordId ,
            "data" : { "redactedText" : returnBlock }
        }
            
        results[ "values" ].append( outputJson )

    # building final output
    jsonResponse = json.dumps( results )

    logging.info( "Final output : " + str( jsonResponse ) + " of type : " + str( type( jsonResponse ) ) )

    return jsonResponse

def fnDetectPII( text ) :

    entityList = []

    apiEndpoint = os.getenv(  "LanguageEndpoint" )
    apiKey = os.getenv( "LanguageKey" )

    apiPath = "language/:analyze-text?api-version=2022-05-01"

    headers = {
        "Content-Type" : "application/json" ,
        "Ocp-Apim-Subscription-Key" : apiKey
    }

    jsonBody = {
        "kind" : "PiiEntityRecognition" ,
        "parameters" : {
            "modelVersion" : "latest" ,
            "piiCategories" : [
                "Person", "PersonType", "PhoneNumber", "Organization", "Address", "Email", "URL", "IPAddress", "ABARoutingNumber", "SWIFTCode" ,
                "CreditCardNumber", "InternationalBankingAccountNumber", "USBankAccountNumber", "USIndividualTaxpayerIdentification", "USUKPassportNumber", 
                "USDriversLicenseNumber", "USSocialSecurityNumber"
            ]
        },
        "analysisInput" : {
            "documents" : [
                {
                "id" : "1" ,
                "language" : "en" ,
                "text" : text
                }
            ]
        }
    }

    requestUrl = apiEndpoint + apiPath

    apiRequest = requests.post( requestUrl, headers = headers, json = jsonBody )

    apiResponse = apiRequest.json()

    # logging.info( "PII API Response : " + str( apiResponse ) )

    if apiResponse[ "kind" ] == "PiiEntityRecognitionResults" :

        redactedText = apiResponse[ "results" ][ "documents" ][ 0 ][ "redactedText" ]

        return redactedText

    else :

        logging.info( "Error running analysis..." )

        assert(), "Error running analysis..."