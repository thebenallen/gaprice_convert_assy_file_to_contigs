
package us.kbase.gapriceconvertassyfiletocontigs;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: ConvertParams</p>
 * <pre>
 * Input parameters for the conversion function.
 * string workspace_name - the name of the workspace from which to take
 *     input and store output.
 * string assembly_file - the name of the input KBaseFile.AssemblyFile to
 *     convert to a ContigSet.
 * string output_name - the name for the produced ContigSet.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "workspace_name",
    "assembly_file",
    "output_name"
})
public class ConvertParams {

    @JsonProperty("workspace_name")
    private String workspaceName;
    @JsonProperty("assembly_file")
    private String assemblyFile;
    @JsonProperty("output_name")
    private String outputName;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("workspace_name")
    public String getWorkspaceName() {
        return workspaceName;
    }

    @JsonProperty("workspace_name")
    public void setWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
    }

    public ConvertParams withWorkspaceName(String workspaceName) {
        this.workspaceName = workspaceName;
        return this;
    }

    @JsonProperty("assembly_file")
    public String getAssemblyFile() {
        return assemblyFile;
    }

    @JsonProperty("assembly_file")
    public void setAssemblyFile(String assemblyFile) {
        this.assemblyFile = assemblyFile;
    }

    public ConvertParams withAssemblyFile(String assemblyFile) {
        this.assemblyFile = assemblyFile;
        return this;
    }

    @JsonProperty("output_name")
    public String getOutputName() {
        return outputName;
    }

    @JsonProperty("output_name")
    public void setOutputName(String outputName) {
        this.outputName = outputName;
    }

    public ConvertParams withOutputName(String outputName) {
        this.outputName = outputName;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((("ConvertParams"+" [workspaceName=")+ workspaceName)+", assemblyFile=")+ assemblyFile)+", outputName=")+ outputName)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
