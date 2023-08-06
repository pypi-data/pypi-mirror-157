# This file is placed in the Public Domain.


"OTP-CR-117/19"


from ..hdl import Commands
from ..obj import Object, get


txt = Object()
txt[1] = "@IntlCrimCourt @Europol @POL_DenHaag @Het_OM ask @KarimKhanQC to reconsider OTP-CR-117/19"
txt[2] = "Elderly Handicapped (Wzd) Psychatric Patients (WvGGZ) Criminals (Wfz)"
txt[3] = "Elderly & Handicapped/Wzd Psychatric Patients/WvGGZ Criminals/Wfz @IntlCrimCourt @KarimKhanQC article 15, reconsider OTP-CR-117/19"
txt[4] = "Elderly & Handicapped/Wzd Psychatric Patients/WvGGZ Criminals/Wfz - @IntlCrimCourt @KarimKhanQC, article 15, reconsider OTP-CR-117/19 - http://genocide.rtfd.io"
txt[5] = "@KarimKhanQC @IntlCrimCourt, Reconsider OTP-CR-117/19 https://genocide.rtfd.io/ #ASP20 #ASP21 #ggz @Het_OM @adnl"
txt[6] = "Prosecutor. Court. Reconsider OTP-CR-117/19. @IntlCrimCourt @KarimKhanQC - https://pypi.org/project/genocide/ #ASP21 #stopgenocide #ggz"
txt[7] = "By law, with the use of poison, killing, torturing, castrating, destroying, in whole or in part, ...."
txt[8] = "all elderly and all handicapped (Wzd), all criminals (Wfz) and all psychiatric patients (WvGGZ) here in the netherlands."
txt[9] = "By law, with the use of poison, killing, torturing, castrating, destroying, in whole or in part, all elderly and all handicapped (Wzd), all criminals (Wfz) and all psychiatric patients (WvGGZ) here in the Netherlands."


def slg(event):
    if event.args:
        event.reply(get(txt, int(event.args[0])))
        return
    event.reply(get(txt, 9))


Commands.add(slg)
