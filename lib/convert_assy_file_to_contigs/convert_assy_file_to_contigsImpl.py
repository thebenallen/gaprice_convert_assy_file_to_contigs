#BEGIN_HEADER
#END_HEADER


class convert_assy_file_to_contigs:
    '''
    Module Name:
    convert_assy_file_to_contigs

    Module Description:
    A KBase module: convert_assy_file_to_contigs
    '''

    ######## WARNING FOR GEVENT USERS #######
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    #########################################
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = "787a649ed8ec35da032e89eb88ab4b4081a5660b"
    
    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        #END_CONSTRUCTOR
        pass
    

    def convert(self, ctx, params):
        """
        :param params: instance of type "ConvertParams" (Input parameters for
           the conversion function. string workspace_name - the name of the
           workspace from which to take input and store output. string
           assembly_file - the name of the input KBaseFile.AssemblyFile to
           convert to a ContigSet. string output_name - the name for the
           produced ContigSet.) -> structure: parameter "workspace_name" of
           String, parameter "assembly_file" of String, parameter
           "output_name" of String
        :returns: instance of type "ConvertOutput" (Output parameters the
           conversion. string report_name - the name of the
           KBaseReport.Report workspace object. string report_ref - the
           workspace reference of the report.) -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN convert
        output = None
        #END convert

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method convert return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK", 'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        del ctx
        #END_STATUS
        return [returnVal]
