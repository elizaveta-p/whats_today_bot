def decode_cyrillic_urls(url: str):
    d = create_table()
    cyrillic_part = url.split('/')[-1]
    for letter in d.keys():
        while letter in cyrillic_part:
            cyrillic_part = cyrillic_part.replace(letter, d[letter])
    url = url.split('/')[:-1]
    url.append(cyrillic_part)
    url = '/'.join(url)
    return url


def create_table():
    s = '''А  0410  D090  208 144  192
    Б  0411  D091  208 145  193
    В  0412  D092  208 146  194
    Г  0413  D093  208 147  195
    Д  0414  D094  208 148  196
    Е  0415  D095  208 149  197
    Ж  0416  D096  208 150  198
    З  0417  D097  208 151  199
    И  0418  D098  208 152  200
    Й  0419  D099  208 153  201
    К  041A  D09A  208 154  202
    Л  041B  D09B  208 155  203
    М  041C  D09C  208 156  204
    Н  041D  D09D  208 157  205
    О  041E  D09E  208 158  206
    П  041F  D09F  208 159  207
    Р  0420  D0A0  208 160  208
    С  0421  D0A1  208 161  209
    Т  0422  D0A2  208 162  210
    У  0423  D0A3  208 163  211
    Ф  0424  D0A4  208 164  212
    Х  0425  D0A5  208 165  213
    Ц  0426  D0A6  208 166  214
    А  0427  D0A7  208 167  215
    Ш  0428  D0A8  208 168  216
    Щ  0429  D0A9  208 169  217
    а  042A  D0AA  208 170  218
    Ы  042B  D0AB  208 171  219
    Ь  042C  D0AC  208 172  220
    Э  042D  D0AD  208 173  221
    Ю  042E  D0AE  208 174  222
    Я  042F  D0AF  208 175  223
    а  0430  D0B0  208 176  224
    б  0431  D0B1  208 177  225
    в  0432  D0B2  208 178  226
    г  0433  D0B3  208 179  227
    д  0434  D0B4  208 180  228
    е  0435  D0B5  208 181  229
    ж  0436  D0B6  208 182  230
    з  0437  D0B7  208 183  231
    и  0438  D0B8  208 184  232
    й  0439  D0B9  208 185  233
    к  043A  D0BA  208 186  234
    л  043B  D0BB  208 187  235
    м  043C  D0BC  208 188  236
    н  043D  D0BD  208 189  237
    о  043E  D0BE  208 190  238
    п  043F  D0BF  208 191  239
    р  0440  D180  209 128  240
    с  0441  D181  209 129  241
    т  0442  D182  209 130  242
    у  0443  D183  209 131  243
    ф  0444  D184  209 132  244
    х  0445  D185  209 133  245
    ц  0446  D186  209 134  246
    ч  0447  D187  209 135  247
    ш  0448  D188  209 136  248
    щ  0449  D189  209 137  249
    ъ  044A  D18A  209 138  250
    ы  044B  D18B  209 139  251
    ь  044C  D18C  209 140  252
    э  044D  D18D  209 141  253
    ю  044E  D18E  209 142  254
    я  044F  D18F  209 143  255
    Ё  0401  D001  208 001  168
    ё  0451  D191  209 145  184'''
    s = [x.strip().split('  ') for x in s.split('\n')]
    d = {f"%{x[2][:2]}%{x[2][2:]}": x[0] for x in s}
    return d
