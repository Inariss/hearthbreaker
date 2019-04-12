

def print_plot(method, data1, d1, data2, d2):

    pos = list(range(len(xaxis)))
    print(pos)
    width=0.3
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ind = np.arange(len(xaxis))
    bar1 = ax.bar(pos, data1, width=0.3, align='center')
    bar2 = ax.bar([p + width for p in pos], data2, width=0.3,align='center')
    ax.set_xticklabels(xaxis, visible=True, rotation='vertical')
    ax.set_ylabel('Accuracy')
    ax.set_title(method)
    ax.set_xticks(ind + width )
    ax.legend( (bar1[0], bar2[0]), (d1, d2) )
    for i, (v1, v2) in enumerate(zip(data1,data2)):
        ax.text(i-.10, v1 + .01, str(v1)+'%', color='black')
        ax.text(i+.18, v2 + .01, str(v2)+'%', color='black')
    plt.tight_layout()
    plt.ylim(0,+110)
    plt.show()