# INPUT PARAMETERS
# _X_RAW_DB, _LO_LIMIT_1
# raw data in csv using db structure, i.e., a single row contains:
# code of representative, code of division, encoded vote (i.e. one of -1, 1, 0, NA)
# for example:
# “Joe Europe”,”Division-007”,”1”


Xsource = read.csv("data/votes-1998-2002.csv")
Xsource$vote_event_id = as.factor(Xsource$vote_event_id)
Xsource$voter_id = as.factor(Xsource$voter_id)
#Xsource = Xsource[c("voter_id","vote_event_id","option")]
Xsource$option2 = rep(0,length(Xsource$option))
Xsource$option2[Xsource$option=='yes'] = 1
Xsource$option2[Xsource$option=='no'] = -1
Xsource$option2[Xsource$option=='abstain'] = -1


#Xrawdb = _X_RAW_DB
Xrawdb = Xsource
# lower limit to eliminate from calculations, e.g., .1; number
lo_limit = .1

# reorder data; divisions x persons
# we may need to install and/or load some additional libraries
# install.packages("reshape2")
# library("reshape2")
# install.packages("sqldf")
# library("sqldf")

#prevent reordering, which is behaviour of acast:
#Xrawdb$V1 = factor(Xrawdb$V1, levels=unique(Xrawdb$V1))
Xrawdb$voter_id = factor(Xrawdb$voter_id, levels=unique(Xrawdb$voter_id))
Xraw = acast(Xrawdb,vote_event_id~voter_id,value.var='option2')
# scale data; divisions x persons (mean=0 and sd=1 for each division)
Xstand=t(scale(t(Xraw),scale=TRUE))

# WEIGHTS
# weights 1 for divisions, based on number of persons in division
w1 = apply(abs(Xraw)==1,1,sum,na.rm=TRUE)/max(apply(abs(Xraw)==1,1,sum,na.rm=TRUE))
w1[is.na(w1)] = 0
# weights 2 for divisions, "100:100" vs. "195:5"
w2 = 1 - abs(apply(Xraw==1,1,sum,na.rm=TRUE) - apply(Xraw==-1,1,sum,na.rm=TRUE))/apply(!is.na(Xraw),1,sum)
w2[is.na(w2)] = 0

# analytical charts for weights:
plot(w1)
plot(w2)
plot(w1*w2)

# weighted scaled matrix; divisions x persons
X = Xstand * w1 * w2

# MISSING DATA
# index of missing data; divisions x persons
I = X
I[!is.na(X)] = 1
I[is.na(X)] = 0

# weighted scaled with NA substituted by 0; division x persons
X0 = X
X0[is.na(X)]=0

# EXCLUSION OF REPRESENTATIVES WITH TOO FEW VOTES (WEIGHTED)
# weights for non missing data; division x persons
Iw = I*w1*w2
# sum of weights of divisions for each persons; vector of length “persons”
s = apply(Iw,2,sum)
pw = s/(t(w1)%*%w2)
# index of persons kept in calculation; vector of length “persons”
pI = pw > lo_limit
# weighted scaled with NA->0 and cutted persons with too few weighted votes; division x persons
X0c = X0[,pI]
# index of missing cutted (excluded) persons with too few weighted votes; divisions x persons
Ic = I[,pI]
# indexes of cutted (excluded) persons with too few votes; divisions x persons
Iwc = Iw[,pI]

# “X’X” MATRIX
# weighted X’X matrix with missing values substituted and excluded persons; persons x persons
C=t(X0c)%*%X0c * 1/(t(Iwc)%*%Iwc) * (sum(w1*w1*w2*w2))
# substitution of missing data in "covariance" matrix (the simple way)
C0 = C
C0[is.na(C)] = 0

# DECOMPOSITION
# eigendecomposition
Xe=eigen(C0)
# W (rotation values of persons)
W = Xe$vectors
# projected divisions into dimensions
Xy=X0c%*%W

# analytical charts of projection of divisions and lambdas
plot(Xy[,1],Xy[,2])
plot(sqrt(Xe$values[1:10]))

# lambda matrix
lambda = diag(sqrt(Xe$values))
lambda[is.na(lambda)] = 0

# projection of persons into dimensions
Xproj = W%*%lambda
    
# analytical chart
plot(Xproj[,1],Xproj[,2])

# lambda^-1 matrix
lambda_1 = diag(sqrt(1/Xe$values))
lambda_1[is.na(lambda_1)] = 0

# Z (rotation values of divisions)
Z = X0c%*%W%*%lambda_1

# analytical charts
# second projection
Xproj2 = t(X0c) %*% Z
# without missing values, they are equal:
plot(Xproj[,1],Xproj2[,1])
plot(Xproj[,2],Xproj2[,2])

# PROJECTION OF PART OF THE LEGISLATIVE TERM INTO THE WHOLE TERM MODEL
# additional parameters:
# _TI,   _LO_LIMIT_2
# lower limit to eliminate from projections (may be the same as lo_limit); number
lo_limitT = _LO_LIMIT_2
# indices whether divisions are in the given part or not
# vector of length div, contains TRUE or FALSE
TI = _TI
# scaling, weighting and missing values treatment
XrawTc = Xraw[,pI]
XrawTc[!TI,] = NA
XTc = (XrawTc - attr(Xstand,"scaled:center"))/attr(Xstand,"scaled:scale")
# Indices of NAs; division x person
TIc = XTc
TIc[!is.na(TIc)] = 1
TIc[is.na(TIc)] = 0
# weights, divisions x persons
XTw0c = XTc * w1 * w2
XTw0c[is.na(XTw0c)] = 0

# weights for non missing data; divisions x persons
TIcw = TIc*w1*w2
# sum of weights of divisions for each persons
s = apply(TIcw,2,sum)
pTw = s/max(s)
# index of persons in calculation
pTI = pTw > lo_limitT

# weighted scaled with NA->0 and cutted persons with too few votes division x persons
XTw0cc = XTw0c[,pTI]
# index of missing data cutted persons with too few votes divisions x persons
TIcc = TIc[,pTI]

# weights of divisions, person x division
aZ = abs(Z)
dweights = t(t(aZ)%*%TIcc / apply(aZ,2,sum))      
dweights[is.na(dweights)] = 0

# projection of persons
XTw0ccproj = t(XTw0cc)%*%Z / dweights

# analytical chart:
plot(XTw0ccproj[,1],XTw0ccproj[,2])

# CUTTING LINES
# additional parameters:
# _N_FIRST_DIMENSIONS
# how many dimensions?
n_first_dimensions = _N_FIRST_DIMENSIONS

# loss function
LF = function(beta0) -1*sum(apply(cbind(y*(x%*%beta+beta0),zeros),1,min))

# preparing variables
normals = Xy[,1:n_first_dimensions]
loss_f = data.frame(matrix(0,nrow=dim(X)[1],ncol=4))
colnames(loss_f)=c("Parameter1","Loss1","Parameter_1","Loss_1")
parameters = data.frame(matrix(0,nrow=dim(X)[1],ncol=3))
colnames(parameters)=c("Parameter","Loss","Direction")

xfull = t(t(Xe$vectors[,1:n_first_dimensions]) * sqrt(Xe$values[1:n_first_dimensions]))

#calculating all cutting lines
for (i in as.numeric(1:dim(X)[1])) {
    beta = Xy[i,1:n_first_dimensions]
    y = t(as.matrix(X[i,]))[,pI]
    x = xfull[which(!is.na(y)),]
    y = y[which(!is.na(y))]
    zeros = as.matrix(rep(0,length(y)))
    # note: “10000” should be enough for any real-life case:
    res1 = optim(c(1),LF,method="Brent",lower=-10000,upper=10000)        
# note: the sign is arbitrary, the real result may be -1*; we need to minimize the other way as well
    y=-y
    res2 = optim(c(1),LF,method="Brent",lower=-10000,upper=10000) 

    # the real parameter is the one with lower loss function
    # note: theoretically should be the same (either +1 or -1) for all divisions(rows), however, due to missing data, the calculation may lead to a few divisions with the other direction
    loss_f[i,] = c(res1$par,res1$value,res2$par,res2$value)
    if (res1$value<=res2$value) {
      parameters[i,] = c(res1$par,res1$value,1)
    } else {
      parameters[i,] = c(res2$par,res2$value,-1)
    }
}
CuttingLines = list(normals=normals,parameters=parameters,loss_function=LF,weights=cbind(w1,w2))

# analytical charts
# cutting lines
# additional parameters:
# _MODULO, _LO_LIMIT_3
# to show only each _MODULO-division (for huge numbers of divisions may be useful to use it) # if set to 1, every division is shown
# _LO_LIMIT_3 is a lower limit used to plot only important divisions; number between [0,1]
lo_limit3 = _LO_LIMIT_3
modulo = _MODULO
plot(Xproj[,1],Xproj[,2])
I = w1*w2 > lo_limit3
for (i in as.numeric(1:dim(X)[1])) {
  if (I[i] && ((i %% modulo) == 0)) {
    beta = CuttingLines$normals[i,]
    beta0 = CuttingLines$parameters$Parameter[i]
        abline(-beta0/beta[2],-beta[1]/beta[2])
  }
}
# normals of cutting lines, possibly with some limitations, e.g. 50, 20: 
plot(CuttingLines$parameters$Parameter/CuttingLines$normals[,1],ylim=c(-50,50))
plot(CuttingLines$parameters$Parameter/CuttingLines$normals[,2],ylim=c(-20,20))
