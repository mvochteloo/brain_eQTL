
# This script runs 4th step to making GeneNetwork: do the DESEQ normalisation

set -e
set -u
module load RPlus
project_dir=
outdir=
config_templates=
jardir=
expression_file=
corrected_dir=
outfile=
main(){
    module load Java/1.8.0_144-unlimited_JCE
    parse_commandline "$@"

    rsync -vP $config_templates/4_DeseqNormalizedData.json $project_dir/configs/

    sed -i "s;REPLACEEXPRFILE;$expression_file;" $project_dir/configs/4_DeseqNormalizedData.json
    sed -i "s;REPLACEOUTDIR;$outdir/;" $project_dir/configs/4_DeseqNormalizedData.json
    sed -i "s;REPLACEPCCORRECTED;$corrected_dir/;" $project_dir/configs/4_DeseqNormalizedData.json

    mkdir -p $(dirname $outdir)

    mkdir -p $(dirname $outdir)
    java -Xmx90g -Xms90g -jar $jardir/RunV13.jar $project_dir/configs/4_DeseqNormalizedData.json
    current_dir=$(dirname "$0")
    Rscript $current_dir/../table_scripts/log2.R -i $outfile -o ${outfile%.txt.gz}.log2.txt

}

usage(){
    # print the usage of the programme
    programname=$0
    echo "usage: $programname -e expression_file -p project_directory -o output_dir"
    echo "  -e      Expression file to remove duplciates from"
    echo "  -p      Base of the project_dir where config files will be written"
    echo "  -o      Output file that will be written"
    echo "  -c      Dir with configuration template files"
    echo "  -f      Name of the outfile"
    echo "  -j      Location of V13 jar file"
    echo "  -z      Directory to write expr files corrected by PCAs to"
    echo "  -h      display help"
    exit 1
}

parse_commandline(){
    # Check to see if at least one argument is given
    if [ $# -eq 0 ]
    then
        echo "ERROR: No arguments supplied"
        usage
        exit 1;
    fi

    while [[ $# -ge 1 ]]; do
        case $1 in
            -p | --project_dir )        shift
                                        project_dir=$1
                                        ;;
            -e | --expression_file )    shift
                                        expression_file=$1
                                        ;;
            -o | --outdir )             shift
                                        outdir=$1
                                        ;;
            -f | --outfile )            shift
                                        outfile=$1
                                        ;;
            -c | --config_templates )   shift
                                        config_templates=$1
                                        ;;
            -j | --jardir )             shift
                                        jardir=$1
                                        ;;
            -z | --corrected_dir )      shift
                                        corrected_dir=$1
                                        ;;
            -h | --help )               usage
                                        exit
                                        ;;
            * )                         echo "ERROR: Undexpected argument: $1"
                                        usage
                                        exit 1
        esac
        shift
    done

    # if -z tests if variable is empty. Make sure the relevant variables are set
    if [ -z "$project_dir" ];
    then
        echo "ERROR: -p/--project_dir not set!"
        usage
        exit 1;
    fi
    if [ -z "$expression_file" ];
    then
        echo "ERROR: -e/--expression_file not set!"
        usage
        exit 1;
    fi
    if [ -z "$outdir" ];
    then
        echo "ERROR: -o/--outdir not set!"
        usage
        exit 1;
    fi
    if [ -z "$outfile" ];
    then
        echo "ERROR: -f/--outfile not set!"
        usage
        exit 1;
    fi
    if [ -z "$jardir" ];
    then
        echo "ERROR: -j/--jardir not set!"
        usage
        exit 1;
    fi
    if [ -z "$config_templates" ];
    then
        echo "ERROR: -c/--config_templates not set!"
        usage
        exit 1;
    fi
    if [ -z "$corrected_dir" ];
    then
        echo "ERROR: -z/--corrected_dir not set!"
        usage
        exit 1;
    fi
}

# [[ ${BASH_SOURCE[0]} = "$0" ]] -> main does not run when this script is sourced
# main "$@" -> Send the arguments to the main function (this way project flow can be at top)
# exit -> safeguard against the file being modified while it is interpreted
[[ ${BASH_SOURCE[0]} = "$0" ]] && main "$@"; exit;






