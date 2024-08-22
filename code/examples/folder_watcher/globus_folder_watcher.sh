#!/bin/bash 
# Example folder watcher script to trigger a Globus file transfer 
source_collection=<SOURCE> 
destination_collection=<DESTINATION> 
 
source_collection_root=/<SEND-DIR> # Root directory of source collection 
source_dir=/<SOURCE-DIR> # Source directory under source_collection_root to be watched 
destination_dir=/<DEST-DIR> # Destination directory under destination collection root 
 
echo "Watching ${source_collection_root}${source_dir}" 
 
/usr/bin/inotifywait -r -m ${source_collection_root}${source_dir} -e moved_to -e close_write | 
    while read dir action file; do 
        if [[ ${file} != "."* ]]; then # Ignore hidden files 
            sleep 1 # Wait one second to let temporary files go away (e.g. vi) 
            if [[ -f ${dir}${file} ]]; then 
                echo "The file '${file}' appeared in directory '${dir}' via '${action}' at $(date)" 
                file_path="$(echo ${dir} | sed s/${source_collection_root//\//\\/}//g)${file}" # Strip source_collection_root from start of file path 
                echo "File path in collection is '${file_path}'" 
                # Transfer the file 
                echo globus transfer "${source_collection}:${file_path}" "${destination_collection}:${destination_dir}${file_path}" 
                globus transfer "${source_collection}:${file_path}" "${destination_collection}:${destination_dir}${file_path}" 
            fi 
        fi 
    done 