import logging, requests, json, os

import azure.functions as func


def main( req: func.HttpRequest ) -> func.HttpResponse:
    
    logging.info( "Python HTTP trigger function processed a request." )

    try:

        body = json.dumps( req.get_json() )
    
    except ValueError :
        
        return func.HttpResponse(
            
            "Invalid body",
            status_code = 400
        
        )
    
    if body :

        # logging.info( "1" )

        result = fnBuildResponse( body )

        # logging.info( "Final verification : " + str( result ) )
        
        return func.HttpResponse( result, mimetype = "application/json" )
    
    else :
        
        return func.HttpResponse(
            
            "Invalid body",            
            status_code = 400
        
        )
    
def fnBuildResponse( json_data ) :

    values = json.loads( json_data )[ 'values' ]

    logging.info( "Input Values : " + str( values ) )
    
    # Prepare the Output before the loop
    results = {}
    results[ "values" ] = []

    translatedList = []

    translatedBlock = ""
    
    for value in values :

        recordId = value[ "recordId" ]

        try :

            # logging.info( "3" )

            assert( "data" in value ), "'data' field is required."

            data = value[ "data" ]

            assert( "merged_content" in data ), "'merged_content' field is required in 'data' object."

            inputText = data[ "merged_content" ]

            redactOutput = fnDetectMetaTagTerms( inputText) # returns list

            logging.info( "Redaction Detection Results : " + str( redactOutput ) )

            outputJson = {
                    "recordId" : recordId ,
                    "data" : {
                        "tagList" : redactOutput
                    }
                }

            results[ "values" ].append( outputJson )

            jsonReponse = json.dumps( results )

            return jsonReponse

        except AssertionError as err :

            return(
                {
                    "recordID" : recordId ,
                    "errors" : [ { "message" : "Error:" + err } ]
                }
            )
        
def fnDetectMetaTagTerms( text ) :

    findingsList = []

    jsonRedactList = {
            "masterSource" : "https://redactionlist.api.dod.gov" ,
            "redactList" : [ {
                "redactCode" : "Top Secret" ,
                "redactStrings" : {
                    "TS1" : "finance" ,
                    "TS2" : "alien" ,
                    "TS3" : "powerpoint",
                    "TS4" : "Top Secret"
                    }
                }, {
                "redactCode" : "For Official Use Only",
                "redactStrings" : {
                    "FOUO1" : "electronic" ,
                    "FOUO2" : "email" ,
                    "FOUO3" : "SharePoint",
                    "FOUO4" : "ACCM"
                    }
                }, {
                "redactCode" : "My God...Its Jason Bourne.",
                "redactStrings" : {
                    "JB1" : "Microsoft" ,
                    "JB2" : "Azure" ,
                    "JB3" : "PowerShell" ,
                    "JB4" : "Kennedy",
                    "JB5" : "Project Neptune Spear"
                    }
                }]
    }

    redactList = jsonRedactList[ "redactList" ]

    for item in redactList :

        typeList = item[ "redactStrings" ]
        typeCode = item[ "redactCode" ]

        for term in typeList.items() :

            termCode = term[ 0 ]
            termString = term[ 1 ]

            if termString in text :

                termIndex = text.index( termString )

                logging.info( "Identified metatag term " + termString + "." )

                findingsList.append( termString )

    if len( findingsList ) <= 0 :

        findingsList.append( "No metatag terms found." )                

    return findingsList