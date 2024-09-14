from matplotlib import pyplot as plt
from scipy.fft import fft, ifft, fftfreq
from sklearn.cluster import DBSCAN
from scipy.io import wavfile
import numpy as np
import pywt

def denoise(time_serie, absolute=True):
    coeffs = pywt.wavedec(time_serie, 'db1', level=8, mode="symmetric")
    sigma = np.median(np.abs(coeffs[8]))/0.6745
    for i in range(6,9):
        D = coeffs[i]
        n = len(D)
        tVisu = np.sqrt(2*np.log(n))*sigma
        coeffs[i] = pywt.threshold(D, tVisu, mode='hard')
        time_serie_rec = pywt.waverec(coeffs, 'db1', mode="symmetric")
        if absolute:
            time_serie_rec = np.abs(time_serie_rec)
    return time_serie_rec

def log_gabor(f, f0, sigma):
    r = np.exp(-np.power(np.log(f/f0),2)/(2*np.power(sigma,2)))
    return r

def gabor(f, f0, sigma):
    r = np.exp(-np.power(f-f0,2)/(2*np.power(sigma,2)))
    return r

def filter_gabor(time_serie, G, plot_spec, samplerate, N):
    time_serie_fft = fft(time_serie)
    T = 1/samplerate
    xf = fftfreq(N, T)[:N//2]
    Fy = time_serie_fft*G
    fym = (ifft(Fy))

    if plot_spec:
        plt.plot(xf, 1.0/N * (np.abs(time_serie_fft[0:N//2])))
        plt.plot(xf, 1.0/N * (np.abs(Fy[0:N//2])))
        #plt.axvline(x=15000, color='r')
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.grid()
        plt.show()

    return fym

def compressor(time_serie, thres, thres2, comp, comp2, dynamic):
    time_serie_out = []
    for i in range(len(time_serie)):
        if time_serie[i] < (-thres):
            xComp = (-thres+(comp*(time_serie[i]+thres)))
        elif time_serie[i] > thres:
            xComp = thres+(comp*(time_serie[i]-thres))
        else:
            if dynamic:
                if time_serie[i] < 0 and time_serie[i] > (-thres2):
                    xComp = (-thres2+(comp2*(time_serie[i]+thres2)))
                elif time_serie[i] > 0 and time_serie[i] < thres2:
                    xComp = thres2+(comp2*(time_serie[i]-thres2))
                else:
                    xComp = time_serie[i]
            else:
                xComp = time_serie[i]
        time_serie_out.append(xComp)
    return time_serie_out


#Verify for aliasing and length of result vector
def clustering(time_serie, window=100):
    zeros = np.zeros(round(window/2))
    time_serie = np.append(zeros, time_serie)
    time_serie = np.append(time_serie, zeros)
    time_serie_length = len(time_serie)
    win_clust = list()
    for i in range(time_serie_length-window):
        y = np.std(time_serie[i:(i+window)])
        win_clust.append(y)
    win_clust = np.asarray(win_clust)
    threshold_clust = 0.05*np.max(win_clust)
    clusters = pywt.threshold(win_clust, threshold_clust, mode='hard')
    return clusters

def zero2one(clusters):
    clusters_length = len(clusters)
    cluster_rise = list()
    for i in range(1, clusters_length-1):
        if clusters[i]!=0 and clusters[i-1]==0:
            cluster_rise.append(i)
    return cluster_rise

def one2zero(clusters):
    clusters_length = len(clusters)
    cluster_down = list()
    for i in range(1, clusters_length-1):
        if clusters[i]!=0 and clusters[i+1]==0:
            cluster_down.append(i)
    return cluster_down

def rangeDistance(audio_file):
    samplerate, time_serie = wavfile.read(audio_file)
    time_serie = time_serie[0:int(np.power(2,(np.floor(np.log2(len(time_serie))))))]
    N = len(time_serie)
    x = range(N)
    sigma = 300 #300
    filter_center = 15000
    freqs = np.array(range(N)) * (samplerate/N)
    G = gabor(freqs, filter_center, sigma)
    #print(samplerate)
    
    time_serie_original = time_serie
    time_serie = time_serie / max(time_serie)
    time_serie_com = compressor(time_serie, 0.2, 0.01, 0.01, 0.01, True)
    
    time_serie_cen = filter_gabor(time_serie, G, False, samplerate, N)
    time_serie_rec = denoise(time_serie_cen, True)
    clusters = clustering(time_serie_rec, window=20) #Avoiding the old proupose of standard deviation windowing
    #clusters = pywt.threshold(time_serie_rec, 0.005, mode='hard') #Recorded from iPhone
    clusters = pywt.threshold(time_serie_rec, 0.02, mode='hard')
    
    change_rise = zero2one(clusters)
    change_down = one2zero(clusters)
    rise_diffs = np.diff(np.array(change_rise))
    down_diffs = np.diff(change_down)
    
    #print(change_rise)
    print(f'Distance Estimation {(np.array(change_rise)[1]-np.array(change_rise)[0])/samplerate*343/2}')


'''
    fig, (axs1, axs2, axs3, axs4) = plt.subplots(4, 1, figsize=(9, 5), layout='constrained',
                        sharex=True)
    

    xlim_plot = (0.1, 0.12)
    axs1.plot(np.asarray(x)/samplerate, time_serie_original)
    axs1.set_xlim(xlim_plot)
    axs1.title.set_text("(a)")

    axs2.plot(np.asarray(x)/samplerate, time_serie_cen)
    axs2.set_xlim(xlim_plot)
    axs2.title.set_text("(b)")

    axs3.plot(np.asarray(x)/samplerate, time_serie_rec)
    axs3.set_xlim(xlim_plot)
    axs3.title.set_text("(c)")

    axs4.plot(np.asarray(x)/samplerate, clusters)
    axs4.set_xlim(xlim_plot)
    axs4.title.set_text("(d)")
    #plt.axvline(x=np.array(change_rise)[1]/samplerate, color='r')

    # Individual Plot
    #plt.plot(np.asarray(x)/samplerate, clusters)
    #plt.xlim(0.05, 0.15)

    fig.supxlabel("Time in seconds")
    fig.supylabel("Amplitude")
    plt.show()
    
    #Fy = fft(fym)
    #plt.plot(xf, 1.0/N * (np.abs(time_serie_fft[0:N//2])))
    #plt.plot(xf, 1.0/N * (np.abs(Fy[0:N//2])))
    #plt.plot(xf, 10*G)
    #plt.axvline(x=10000, color='r')
    #plt.grid()
    #plt.show()
'''


if __name__ == "__main__":
    #audio_folder = '/home/ruben/Proyectos/Github/vehicle-robot/python_codes/'
    #audio = '100cm_tri_15khz.wav'
    audio_folder = '/home/ruben/Documentos/DCAT/Sonar/Interfaz/30cm/'
    audio = 'Sin_1500_10.wav'

    audio_files = [
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/20cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/20cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/20cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/20cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/20cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/40cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/40cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/40cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/40cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/40cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/60cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/60cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/60cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/60cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/60cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/80cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/80cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/80cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/80cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/80cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/100cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/100cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/100cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/100cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/100cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/120cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/120cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/120cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/120cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/120cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/140cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/140cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/140cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/140cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/140cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/160cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/160cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/160cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/160cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/160cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/180cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/180cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/180cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/180cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/180cm_05.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/200cm_01.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/200cm_02.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/200cm_03.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/200cm_04.wav',
        '/home/ruben/Documentos/DCAT/Sonar/Interfaz/vsSensoresSwt/200cm_05.wav'   
    ]
    for file in audio_files:
        rangeDistance(file)
    