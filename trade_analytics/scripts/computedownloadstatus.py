

import computeapp.models as cmpmd


def run():
    # Download all data
    for compsess in cmpmd.ComputeSession.objects.all():

        # cmpmd.ComputeStatus.objects.filter(ComputeSession_id=compsess.id)
        D = {}
        for status in cmpmd.ComputeStatus.Compute_status_choices:
            D[status[0]] = cmpmd.ComputeStatus.objects.filter(
                ComputeSession_id=compsess.id, ComputeStatus=status[0]).count()

        ss = compsess.Name + " " +\
            str(compsess.Starttime) + " " +\
            str(compsess.Endtime)
        for key, value in D.items():
            ss = ss + " " + key + " : " + str(value)
        print ss
