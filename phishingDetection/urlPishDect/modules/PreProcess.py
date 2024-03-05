from modules.FeatureExtraction import FeatureExtractionURLS
import pandas as pd
import threading


class PreProcessURLS:
    
    def __init__(self, fileName = "df1.csv" , chunk_size = 3):

        df = pd.read_csv(fileName)
        
        chunk_indices  = self.process_dataframe_in_chunks( df, chunk_size = chunk_size )
        
        self.launchThreads(df ,chunk_indices)

        print("Processing complete.")

    

    def process_dataframe_in_chunks(self, df, chunk_size=10):
        
        total_iterations = len(df)  # Total number of rows in the DataFrame
        chunk_indices = []  # init  df chunk List 

        chunkInc = int(total_iterations / chunk_size)

        i = 0

        while i < total_iterations:  
            
            end = min(i + chunkInc-1, total_iterations)  # Ensure the end index doesn't exceed the total number of rows
            chunk_indices.append((i, end))

            i += min(chunkInc , total_iterations)  

        print("chunk_indices",chunk_indices)
        print("number of Chuncks = > ",len(chunk_indices))

        return chunk_indices
    

    def launchThreads(self, df , chunk_indices):

        threads = []  

        for start, end in chunk_indices:

            fName = "output/chunk_"+str(start) + "-"+str(end)+".csv"
            df_chunk = df[start:end]  

            thread = threading.Thread(target=self.process_chunk, args=(df_chunk,fName,))  # Create a thread for processing the chunk
            
            thread.start()  
            threads.append(thread)  

        for thread in threads:
            thread.join()
        
    
    # Function to process a chunk of DataFrame
    def process_chunk(self, df_chunk,filename ="processedData.csv",bufferPush=15):
        
        feature = []
        result =[]
        
        for index, row in df_chunk.iterrows():

            url = row['url']
            label = row['label']
            
            result = self.append_feature_with_timeout(url, label)

            if(result):
                feature.append(result)

                if(len(feature) > bufferPush):

                    FeatureExtractionURLS().write_features_to_csv(feature,filename)
                    feature = []

        if(feature):
            FeatureExtractionURLS().write_features_to_csv(feature,filename)

    
    def append_feature_with_timeout(self, url, label ,timeout=55):
        
        result = []

        def append_feature_thread():
            nonlocal result
            result = FeatureExtractionURLS().appendFeature(url, label)
        
        thread = threading.Thread(target=append_feature_thread)
        thread.start()

        # Wait for the thread to finish or timeout
        thread.join(timeout)

        # If the thread is still alive after the timeout, it means appendFeature took too long
        if thread.is_alive():
            print("Took too long. Skipping to the next iteration.")
            return []
        
        else:
            # If the thread finished return
            return result
        
    
        
