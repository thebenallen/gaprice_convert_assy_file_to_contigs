/*
A KBase module: convert_assy_file_to_contigs
*/

module gaprice_convert_assy_file_to_contigs {

    /* Input parameters for the conversion function.
        string workspace_name - the name of the workspace from which to take
            input and store output.
        string assembly_file - the name of the input KBaseFile.AssemblyFile to
            convert to a ContigSet.
        string output_name - the name for the produced ContigSet.
    */
    typedef structure {
        string workspace_name;
        string assembly_file;
        string output_name;
    } ConvertParams;

    /* Output parameters the conversion.
        string report_name - the name of the KBaseReport.Report workspace
            object.
        string report_ref - the workspace reference of the report.
    */
    typedef structure {
        string report_name;
        string report_ref;
    } ConvertOutput;

    funcdef convert(ConvertParams params) returns(ConvertOutput output)
        authentication required;
};
