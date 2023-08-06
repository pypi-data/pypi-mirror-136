=====
Usage
=====

To use Python Interface to Cologne Digital Sanskrit Lexicon (CDSL) in a project::

    import pycdsl

    CDSL = pycdsl.CDSLCorpus()
    CDSL.setup()

    results = CDSL.MW.search("राम")


To use REPL Interface to Cologne Digital Sanskrit Lexicon (CDSL)::

    $ cdsl


Example of a :code:`cdsl` REPL Session::

    Cologne Sanskrit Digital Lexicon (CDSL)
    Type any keyword to search in the selected lexicon. (help or ? for list of options)
    Loaded 23 dictionaries.

    (CDSL::None) use MW
    (CDSL::MW) हृषीकेश

    <MWEntry: 263922: हृषीकेश = हृषी-केश a   See below under हृषीक.>
    <MWEntry: 263934: हृषीकेश = हृषीकेश b m. (perhaps = हृषी-केश cf. हृषी-वत् above) id. (-त्व n.), MBh.; Hariv. &c.>
    <MWEntry: 263935: हृषीकेश = N. of the tenth month, VarBṛS.>
    <MWEntry: 263936: हृषीकेश = of a Tīrtha, Cat.>
    <MWEntry: 263937: हृषीकेश = of a poet, ib.>
    <MWEntry: 263938: हृषीकेश = lord of the senses (said of Manas), BhP.>

    (CDSL::MW) show 263938

    <MWEntry: 263938: हृषीकेश = lord of the senses (said of Manas), BhP.>

    (CDSL::MW) scheme itrans

    Input scheme: itrans

    (CDSL::MW) hRRiSIkesha

    <MWEntry: 263922: हृषीकेश = हृषी-केश a   See below under हृषीक.>
    <MWEntry: 263934: हृषीकेश = हृषीकेश b m. (perhaps = हृषी-केश cf. हृषी-वत् above) id. (-त्व n.), MBh.; Hariv. &c.>
    <MWEntry: 263935: हृषीकेश = N. of the tenth month, VarBṛS.>
    <MWEntry: 263936: हृषीकेश = of a Tīrtha, Cat.>
    <MWEntry: 263937: हृषीकेश = of a poet, ib.>
    <MWEntry: 263938: हृषीकेश = lord of the senses (said of Manas), BhP.>

    (CDSL::MW) info

    CDSLDict(id='MW', date='1899', name='Monier-Williams Sanskrit-English Dictionary')

    (CDSL::MW) exit

    Bye
