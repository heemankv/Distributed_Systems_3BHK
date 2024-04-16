
from random import sample

def initialize_centroids(k):        
        centroids = []
        count=0
        while(count!=k):
            points=get_random_data_point()
            if(points not in centroids):
                centroids.append(get_random_data_point())     
                count+=1       
        return centroids

def get_random_data_point(): 
    #TODO: centroids should not be same 
    return (sample(range(10), 1)[0], sample(range(10), 1)[0])

a= [[1,1],[1,2],[1,3],[3,4],[6,7],[5,2]]
b= [[1,1],[1,2],[1,3],[6,7],[3,4],[5,2]]

print(a==b)