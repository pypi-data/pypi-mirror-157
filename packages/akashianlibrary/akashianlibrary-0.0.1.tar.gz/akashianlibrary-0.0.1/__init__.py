# programme on conditional probability

class akashian:
    def __init__(self):
        self.a = a
        self.b = b
        self.li = li
        self.head = head
        self.tail = tail


    def conditional_probabillity(a, b):
        import random
        a = [0, 1]
        b = [0, 1]
        atleast = 0
        head_count = 0
        notr = int(input("Enter the number: "))
        for i in range(notr):
            n1 = random.choice(a)
            if (n1 == 0):
                n2 = 1
                atleast += 1
                continue
            else:
                n2 = random.choice(b)
                if (n2 == 1):
                    head_count += 1
                else:
                    atleast += 1
                    continue
        print((head_count / atleast) * 100)
    # li = [0,1]
    # head = 0
    # tail = 0
    def fixed_probability_head_and_tails(li,head,tail):
        import random
        head = 0
        tail = 0
        for i in range(0, 1000):
            n = random.choice(li)
            if (n):
                head += 1
            else:
                tail += 1
        print("Probability of head count in percentage:", head / 1000 * 100)
        for i in range(0, 10000):
            n = random.choice(li)
        if (n):
            head += 1
        else:
            tail += 1
            print("Probability of head count in percentage:", head / 10000 * 100)

            print(fixed_probability_head_and_tails(li, head, tail))
        # li = [1, 2, 3, 4, 5, 6]
    def frequency_occurance(li):
        import random
        li = [1, 2, 3, 4, 5, 6]
        die1 = 0
        # input1=int(input("Enter"))
        for i in range(0, 1000):
            n = random.choice(li)
            if (n == 1):
                die1 += 1
        print("No of 1s: ", die1)
        print("No of trials: ", 1000)
        print("Probability of getting 1: ", die1 / 1000 * 100)
        for i in range(0, 10000):
            n = random.choice(li)
            if (n == 1):
                die1 += 1
        print("No of 1s: ", die1)
        print("No of trials: ", 10000)
        print("Probability of getting 1: ", die1 / 10000 * 100)
        for i in range(0, 100000):
            n = random.choice(li)
            if (n == 1):
                die1 += 1
        print("No of 1s: ", die1)
        print("No of trials: ", 100000)
        print("Probability of getting 1: ", die1 / 100000 * 100)

    def normal_dist(x, mean, sd):
        prob_density = (np.pi * sd) * np.exp(-0.5 * ((x - mean) / sd) ** 2)
        return prob_density
    # from matplotlib import pyplot as plt
    # import numpy as np

    # Calculate mean and Standard deviation.
    mean = np.mean(x)
    sd = np.std(x)
    # Apply function to the data.
    pdf = normal_dist(x, mean, sd)
    # Plotting the Results
    plt.plot(x, pdf, color='red')
    plt.xlabel('Data points')
    plt.ylabel('Probability Density')
    plt.show()

   def binomail_probability_distribution(self):
       #import matplotlib.pyplot as plt
       # import numpy as np
       # fixing the seed for reproducibility
       # of the result
       np.random.seed(10)
       size = 10000
       # drawing 10000 sample from
       # binomial distribution
       sample = np.random.binomial(20, 0.5, size)
       bin = np.arange(0, 20, 1)
       plt.hist(sample, bins=bin, edgecolor='blue')
       plt.title("Binomial Distribution")
       plt.show()

   def poission_distribution(self):
       #from scipy.stats import poisson
       # importing numpy as np
       #import numpy as np
       # importing matplotlib as plt
       #import matplotlib.pyplot as plt
       # creating a numpy array for x-axis
       x = np.arange(0, 100, 0.5)
       # poisson distribution data for y-axis
       y = poisson.pmf(x, mu=40, loc=10)
       # plotting the graph
       plt.plot(x, y)
       # showing the graph
       plt.show()

   def pearson_correlation_distribution(self):
       #import pandas as pd
      # from scipy.stats import pearsonr
       # Import your data into Python
       df = pd.read_csv("Auto.csv")
       # Convert dataframe into series
       list1 = df['weight']
       list2 = df['mpg']
       # Apply the pearsonr()
       corr, _ = pearsonr(list1, list2)
       print('Pearsons correlation: %.3f' % corr)


   def simple_linear_regression(X, Y, n):
        sum_X = 0
        sum_Y = 0
        sum_XY = 0
        squareSum_X = 0
        squareSum_Y = 0
        c = 0
        i = 0
        while i < n:
        # sum of elements of array X.
            sum_X = sum_X + X[i]
        # sum of elements of array Y.
            sum_Y = sum_Y + Y[i]
        # sum of X[i] * Y[i].
            sum_XY = sum_XY + X[i] * Y[i]
        # sum of square of array elements.
            squareSum_X = squareSum_X + X[i] * X[i]
            squareSum_Y = squareSum_Y + Y[i] * Y[i]
            i = i + 1
        # use formula for calculating correlation
        # coefficient.
            byx = ((sum_XY * n) - (sum_X * sum_Y)) / ((squareSum_X * n) - (sum_X *
                                                                       sum_X))
            bar_X = sum_X / n
            bar_Y = sum_Y / n
            c = (bar_Y) - (byx * (bar_X))

   def checking_average(age):
        sum = 0
        for i in range(10):
            sum = sum + float(input('Enter a age: '))
        average = sum / 10
        if (average == 30):
            print("Yes the average Age is 30")
        else:
            print("No the average age is not 30")

   def calculate_t_test_for_2_independant(data1,data2,alpha):
        #from math import sqrt
        #from numpy.random import seed
        #from numpy.random import randn
        #from numpy import mean
        #from scipy.stats import sem
       # from scipy.stats import t
        #mean1, mean2 = mean(data1), mean(data2)
        # calculate standard errors
        se1, se2 = sem(data1), sem(data2)
        # standard error on the difference between the samples
        sed = sqrt(se1 ** 2.0 + se2 ** 2.0)
        # calculate the t statistic
        t_stat = (mean1 - mean2) / sed
        # degrees of freedom
        df = len(data1) + len(data2) - 2
        # calculate the critical value
        cv = t.ppf(1.0 - alpha, df)
        # calculate the p-value
        p = (1.0 - t.cdf(abs(t_stat), df)) * 2.0
        #  return everything
        return t_stat, df, cv, p

        # seed the random number generator
        seed(1)
        # generate two independent samples
        data1 = 5 * randn(100) + 50
        data2 = 5 * randn(100) + 51
        # calculate the t test
        alpha = 0.05
        t_stat, df, cv, p = independent_ttest(data1, data2, alpha)
        print('t=%.3f, df=%d, cv=%.3f, p=%.3f' % (t_stat, df, cv, p))
        print('interpret result via critical value=>')
        # interpret via critical value
        if abs(t_stat) <= cv:
            print('Accept null hypothesis that the means are equal.')
        else:
            print('Reject the null hypothesis that the means are equal.')
            # interpret via p-value
            print('interpret result via p value=>')
        if p > alpha:
            print('Accept null hypothesis that the means are equal.')
        else:
            print('Reject the null hypothesis that the means are equal.')

   def correlation_coefficent(x, y, n):
        """ import pandas as pd
        import scipy.stats
        import math
        x = [15, 18, 21, 15, 21]
        y = [25, 25, 27, 27, 27]
"""
        sum_x = 0
        sum_y = 0
        sum_xy = 0
        squaresum_x = 0
        squaresum_y = 0
        i = 0
        while i < n:
            sum_x = sum_x + x[i]
            sum_y = sum_y + y[i]
            sum_xy = sum_xy + x[i] * y[i]
            squaresum_x = squaresum_x + x[i] * x[i]
            squaresum_y = squaresum_y + y[i] * y[i]
            i = i + 1
            corr = (float)(n * sum_xy - sum_x * sum_y) / (float)(
                math.sqrt((n * squaresum_x - sum_x * sum_x) * (n * squaresum_y - sum_y *
                                                               sum_y)))
        return corr


    def checking average_30(data):
    # You have 10 ages and you are checking if average age is 30 or Not
    from scipy.stats import ttest_1samp
    import numpy as np
        ages = [32, 34, 29, 22, 39, 38, 37, 38, 36, 30, 27, 22, 22]
        ages_mean = np.mean(ages)
        print("ages observerd mean", ages_mean)
        tset, pval = ttest_1samp(ages, 30)  # Population mean 30
        print("p-values", pval)
        if pval < 0.05:
        # alpha value is 0.05 or 5% level of significance
           print(" we are rejecting null hypothesis")
        else:
           print("we are accepting the null hypothesis")


    def spearmans_rank_correlation(x, y):
        xranks = pd.Series(x).rank()
        print("Rankings of X:")
        print(xranks)
        yranks = pd.Series(y).rank()
        print("Rankings of Y:")
        print(yranks)
        print("Spearman's Rank correlation:", scipy.stats.pearsonr(xranks, yranks)[0])
        n = len(x)
       spearmans_rank_correlation(x, y)
       print("correlation", correlation_coefficent(x, y, n))







