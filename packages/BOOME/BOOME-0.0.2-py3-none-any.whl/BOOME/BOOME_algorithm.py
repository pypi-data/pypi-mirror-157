
import numpy as np
import pandas as pd
import math

from scipy.stats import norm
from numpy.linalg import inv

def ME_Generate(n,beta,cov,X,gamma):
    p=len(beta)
    def xi(p):
        def cov(p):
            cov=[]
            for i in range(p):
                n=[0]*i
                n.append(1)
                for j in range(i+1,p):
                    n.append(0.5**(j-i))
                cov.append(n)
            cov=np.array(cov)
            cov1=cov.T-np.diag(cov.diagonal())
            return  (cov+cov1)
        
        def mean(p):
            zero=[0]
            return zero*p 
    
        return np.random.multivariate_normal(mean(p),cov(p))
   

    def beta_0(p):
        return beta
    def data(p,n):
        data=pd.DataFrame({})
        for i in range(n): 
            x=X[i]
            scalar=np.dot(x,beta_0(p))
            outcome=math.exp(scalar)/(1+math.exp(scalar))
        
            x=list(x)
            x.append(outcome)
            if outcome>=0.5:
                x.append(1)
            else:
                x.append(0)
            
            x=pd.DataFrame(x).T
            data=pd.concat([data,x],axis=0)
        
        data=data.set_axis(range(n), axis=0)
        data=data.set_axis(range(1,p+3), axis=1)
        data=data.rename({p+1: 'prob', p+2:'y'}, axis=1)
                  
        return data
    


# new data1 (y unrevised)--------------------------------------------------------------------


    def new_data1(df):
        p=df.shape[1]-2
        n=len(df)
    
        prob=np.array(df['prob'])
        x=np.array(df.drop(['y','prob'],axis=1))
    
        y_new=[]
        m=[]
    
        for i in range(n):
            m_list=[]
            scalar=math.exp(gamma[0]+np.dot(x[i],np.array(gamma[1])))
            scalar1=math.exp(gamma[2]+np.dot(x[i],np.array(gamma[3])))
            matrix=np.array([[1/(1+scalar),scalar/(1+scalar)],[scalar1/(1+scalar1),1/(1+scalar1)]])
            prob_old=np.array([[prob[i]],[1-prob[i]]])
            prob_new=np.dot(matrix,prob_old)
            
            m_list.append(matrix[0][1])
            m_list.append(matrix[1][0])
            m_list=np.array(m_list)
            m.append(m_list)
        
            if prob_new[0]>prob_new[1]:
                y_new.append(1)
            else:
                y_new.append(0)
        y_new_data=pd.DataFrame(np.array(y_new))
    
        y_new_data.columns=['y']
        y_new_data=y_new_data.set_axis(range(n), axis=0)
    
    
        data=pd.concat([df.drop('y',axis=1), y_new_data] ,axis=1)
        m=np.array(m)
        
        return data,m

    
# error (x unrevised)------------------------------------------------------------------
    def x_error(df):
        x=np.array(df.drop(['y','prob'],axis=1))
        p=df.shape[1]-2
        n=len(df)
    
        def mean(p):
            zero=[0]
            return zero*p
    
    
        data=pd.DataFrame({})
        for i in range(n):
            e=np.array(np.random.multivariate_normal(mean(p),cov))
            x=np.array(df.T[i][:p])+e
        
            x=pd.DataFrame(x).T
            data=pd.concat([data,x],axis=0)
        
        data=data.set_axis(range(n), axis=0)
        data=data.set_axis(range(1,p+1), axis=1)
    
        return data
    
# data x_unrevised and y, y*, y**------------------------------------------------------------

    def data_error(df):
        drop=df[['y']]
        data=pd.concat([error,drop],axis=1)
        return data

#-----------------------------------------------------------------------------------------------
      
    
    df1=data(p,n)
    error=x_error(df1)
    y_true=df1['y']
    df2=new_data1(df1)
    df2_star=data_error(df2[0])

    
    return df2[1],df2_star
         










def LR_Boost(X,Y,ite,thres,correct_X,correct_Y,pr,lr,matrix):
    y1=pd.DataFrame(Y)
    y1.columns=['y']
    df=pd.concat([X,y1],axis=1)
    
    p=df.shape[1]-1
    n=len(df)
# g function ----------------------------------------------------------------------
    def g(beta,df):
    
        y=np.array(df['y'])
        x=np.array(df.drop(['y'],axis=1))    
        sigma=np.array([0]*p)
        for i in range(n):
            try:
                scalar=(math.exp(np.dot(x[i],beta)))
            except :
                scalar=8.218407461554972e+307
            sigma=sigma+ (-x[i]*scalar/(1+scalar)+y[i]*x[i])  
        return sigma
# delta function ----------------------------------------------------------------------
    def delta_function(beta,df):
    

        y=np.array(df['y'])
        x=np.array(df.drop(['y'],axis=1))
    
    
        sigma=np.array([0]*p)
        for i in range(n):
            scalar1=np.dot(x[i],beta)
            scalar2= y[i]* (np.dot((np.dot(beta,matrix)),beta))
            mul=x[i]+y[i]*(np.dot(beta,matrix))
            scalar=math.exp(scalar1+scalar2)
                              
            sigma=sigma+(-mul*scalar/(1+scalar)+y[i]*mul)
        
        return sigma

# threeboost-----------------------------------------------------------------------
    def threeboost(df,ite,thres):
    
        delta=np.array([0.0]*p)
        for i in range(ite):
            g_function=g(delta,df)
            maxima=max(abs(g_function))
        
            for j in range(len(g_function)):
                if abs(g_function[j])>=(thres*maxima):
                    delta[j]=delta[j]+g_function[j]*lr
                else :
                    delta[j]=delta[j] 
        delta=np.where(abs(delta)>0.01,delta,0)
        return delta  
# threeboost_delta-----------------------------------------------------------------------    
    def threeboost_delta(df,ite,thres):
    
        delta=np.array([0.0]*p)
        for i in range(ite):
            g_function=delta_function(delta,df)
            maxima=max(abs(g_function))
        
            for j in range(len(g_function)):
                if abs(g_function[j])>=(thres*maxima):
                    delta[j]=delta[j]+g_function[j]*lr
                else:
                    delta[j]=delta[j]
                    
        delta=np.where(abs(delta)>0.01,delta,0)
        return delta      

# new data2  (y revised)------------------------------------------------------------------------------
    def new_data2(df):
       
        y_old=np.array(df['y'])
        x=np.array(df.drop(['y'],axis=1))
    
        y_new=[]
    
        for i in range(n):
            p1=pr[i][0]
            p2=pr[i][1]
            y=((y_old[i]-p1)/(1-p1-p2))
            if y>=0.5:
                y_new.append(1)
            else:
                y_new.append(0)
        
        
        
        y_new_data=pd.DataFrame(np.array(y_new))
    
        y_new_data.columns=['y']
        y_new_data=y_new_data.set_axis(range(n), axis=0)
    
    
        data=pd.concat([df.drop('y',axis=1), y_new_data] ,axis=1)
        
        return data



#-----------------------------------------------------------------------------------------------
  
    df2_star=df    
    df3_star=new_data2(df2_star)
    y_error=df2_star['y']
    
    
    if correct_X==1 and correct_Y==1:
        result=threeboost_delta(df3_star,ite,thres)
        y_new=df3_star['y']
        x_new=df3_star.drop(['y'],axis=1)
    elif correct_X==1 and correct_Y==0:
        result=threeboost_delta(df2_star,ite,thres)
        y_new=df2_star['y']
        x_new=df2_star.drop(['y'],axis=1)
    elif correct_X==0 and correct_Y==1:
        result=threeboost(df3_star,ite,thres)
        y_new=df3_star['y']
        x_new=df3_star.drop(['y'],axis=1)
    else:
        result=threeboost(df2_star,ite,thres)
        y_new=df2_star['y']
        x_new=df2_star.drop(['y'],axis=1)
    
    number=[]
    for i in range(len(result)):
        if result[i]!=0:
            number.append(i+1)




        

    return print('estimated coefficient :{}'.format(list(result))+'\n'+
                  'predictors:{}'.format(list(number))+'\n'+
                 'number of predictors:{}'.format(len(number)))






def PM_Boost(X,Y,ite,thres,correct_X,correct_Y,pr,lr,matrix):
    y1=pd.DataFrame(Y)
    y1.columns=['y']
    df=pd.concat([X,y1],axis=1)
    
    p=df.shape[1]-1
    n=len(df)

# g function ----------------------------------------------------------------------
    def g(beta,df):
     
        y=np.array(df['y'])
        x=np.array(df.drop(['y'],axis=1))    
        sigma=np.array([0]*p)
        for i in range(n):
            scalar=np.dot(x[i],beta)
            cdf=norm.cdf(scalar)
            exp=math.exp((scalar**2)*(-0.5))
            pi=math.pi
            common=x[i]*((2*pi)**(-0.5))*exp
            cal=common*(y[i]/cdf+(y[i]-1)/(1-cdf))
            sigma=sigma+ cal 
        return sigma

# threeboost-----------------------------------------------------------------------
    def threeboost(df,ite,thres):
        
        delta=np.array([0.0]*p)
        for i in range(ite):
            g_function=g(delta,df)
            maxima=max(abs(g_function))
        
            for j in range(len(g_function)):
                if abs(g_function[j])>=(thres*maxima):
                    delta[j]=delta[j]+g_function[j]*lr
                else :
                    delta[j]=delta[j]   
        delta=np.where(abs(delta)>0.01,delta,0)
        return delta  

# new data2  (y revised)------------------------------------------------------------------------------
    def new_data2(df):
       
        y_old=np.array(df['y'])
        x=np.array(df.drop(['y'],axis=1))
    
        y_new=[]
    
        for i in range(n):
            p1=pr[i][0]
            p2=pr[i][1]
            y=((y_old[i]-p1)/(1-p1-p2))
            if y>=0.5:
                y_new.append(1)
            else:
                y_new.append(0)
        
        
        
        y_new_data=pd.DataFrame(np.array(y_new))
    
        y_new_data.columns=['y']
        y_new_data=y_new_data.set_axis(range(n), axis=0)
    
    
        data=pd.concat([df.drop('y',axis=1), y_new_data] ,axis=1)
        
        return data
    
# x_revised  (x revised)------------------------------------------------------------------------------
    def x_revised(df):
        
        y=df[['y']]
        x=np.array(df.drop(['y'],axis=1))
    
        
        mean=x.mean(0)
        covariance=np.cov(x.T)
        inverse=inv(covariance)
        
        data=pd.DataFrame({})
        for i in range(n):
            x_new_list=mean+np.dot((covariance-matrix),np.dot(inverse,(x[i]-mean)))
            x_new_list=pd.DataFrame(x_new_list).T
            data=pd.concat([data,x_new_list],axis=0)
        
        
        data=data.set_axis(range(n), axis=0)
        data=data.set_axis(range(1,p+1), axis=1)
        data=pd.concat([data,y],axis=1)
        
        return data
#-----------------------------------------------------------------------------------------------
      
    
    df2_star=df    
    df3_star=new_data2(df2_star)
    df3_star_star=x_revised(df3_star)
    df2_star_star=x_revised(df2_star)
    y_error=df2_star['y']

   
    if correct_X==1 and correct_Y==1:
        data=df3_star_star
    elif correct_X==1 and correct_Y==0:
        data=df2_star_star
    elif correct_X==0 and correct_Y==1:
        data=df3_star
    else:
        data=df2_star
        
    result=threeboost(data,ite,thres)
    y_new=data['y']
    x=np.array(data.drop(['y'],axis=1))
    result=np.array(result) 
    number=[]
    for i in range(len(result)):
        if result[i]!=0:
            number.append(i+1)
    number_set=set(number)


        
    return print('estimated coefficients:{}'.format(list(result))+'\n'+
                  'predictors:{}'.format(list(number))+'\n'+
                 'number of predictors:{}'.format(len(number)))

                






