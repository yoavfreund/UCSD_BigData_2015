###Some other points that keep coming up ###

- To get a list of dataflows and their status the preferred method is `utils/find_waiting_flow.py`.  
Other options are [here](AccessingNameNodes.md) and 
[aws cookbook](http://seed.ucsd.edu/mediawiki/index.php/AWS_CookBook)

- You cannot write to a file in hdfs (aws doesnt let us do that), hence write to s3 and pull from there. 
- Pandas, scikit-learn, numpy etc are now pre installed in the
  clusters. You can manually install any new package that you might
  require by sshing into the namenode as explained [here](HadoopClusterAccess)
  You can manually import files to hdfs after sshing into the namenode as well.
- Entire s3 directory can be read as input by giving the s3 directory path as input alongwith the forward slash i.e $input = s3://dse-sachin/inp_directory/ - Thanks Jennifer
- Professor has detailed the process of getting logs using get_emr_logs.py here - [getting logs](http://seed.ucsd.edu/mediawiki/index.php/AccessingLogsUsingOurScripts)
- Its generally helpful to profile your code to optimize execution time. Kevin has explained it in HipChat and you can read more on profilers here - Profilers - Thanks Kevin
