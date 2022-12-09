import matplotlib.pyplot as plt
import scipy.optimize as opt

import data.config as config
from main import main


xPoints = []
yPointsVideo = []
yPointsSearching = []

for i in range(1,30):
    #config.videoDuration = 

    try:
        currentProgram = main()
        currentProgram.printInfo()

        yPointsVideo.append(currentProgram.timeSpent)
        yPointsSearching.append(currentProgram.timeSearching)
        
        xPoints.append(config.videoDuration)

    except:
        None

    #xPoints.append(i)
    #yPoints.append(i*10)

plt.scatter(xPoints, yPointsVideo, c ="blue")
plt.scatter(xPoints, yPointsSearching, c = "red")

# The actual curve fitting happens here
#optimizedParameters, pcov = opt.curve_fit(func, xdata, ydata);

# Use the optimized parameters to plot the best fit
#plt.plot(xdata, func(xdata, *optimizedParameters), label="fit");

# coefficients = np.polyfit(x, y, 3)

# Calculate the polynomial

# poly = np.poly1d(coefficients)

# new_x = np.linspace(x[0], x[-1])

# Calculate new x and y values

# new_y = poly(new_x)



# plt.plot(x, y, "o", new_x, new_y)

plt.xlabel("Video time duration (s)")
plt.ylabel("Video processing duration (s)")

# To show the plot
plt.show()

