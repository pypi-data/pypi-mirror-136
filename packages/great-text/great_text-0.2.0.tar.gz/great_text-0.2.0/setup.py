# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['great_text']

package_data = \
{'': ['*']}

install_requires = \
['pyfiglet>=0.8.post1,<0.9', 'termcolor>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'great-text',
    'version': '0.2.0',
    'description': 'Add font and color to your Python text.',
    'long_description': '# Great Text\n\nThis package enables you to print great text like below\n![image](https://github.com/DeepakDarkiee/great-text/blob/master/great.png?raw=True).\n\ngreat-text requires [Python](https://www.python.org/downloads/release/python-395/) v8+ to run.\n\nTo install this package, use\n\n```bash\npip install great-text\n```\n\n## RUN\n\nWant to contribute? Great!\n\nOpen your favorite Terminal and run these commands.\n\nFirst Tab:\n\n```sh\ntouch example.py\n```\n\nOpen your favorite text editor and write\n\n```sh\nfrom great_text import great_text\n```\n\ncall the function great-text with arguments given bellow\n\n```sh\ngreat_text("Hello","red","isometric2")\n```\n\nthe code will look like this\n\n```sh\nfrom great_text import great_text\n\ngreat_text("Hello","red","isometric2",)\n\n```\n\n> Note: `You can change text ,color and fonts`\n\nNow RUN\n\n```sh\npython example.py\n```\n\nPossible Text colors are Listed below:\n\n```sh\ngrey\nred\ngreen\nyellow\nblue\nmagenta\ncyan\nwhite\n```\n\nPossible Fonts are Listed below:\n\n> Note: `fonts are optional`\n\n```sh\n1943____\n3-d\n3x5\n4x4_offr\n5lineoblique\n5x7\n5x8\n64f1____\n6x10\n6x9\na_zooloo\nacrobatic\nadvenger\nalligator\nalligator2\nalphabet\naquaplan\narrows\nasc_____\nascii___\nassalt_m\nasslt__m\natc_____\natc_gran\navatar\nb_m__200\nbanner\nbanner3\nbanner3-D\nbanner4\nbarbwire\nbasic\nbattle_s\nbattlesh\nbaz__bil\nbeer_pub\nbell\nbig\nbigchief\nbinary\nblock\nbrite\nbriteb\nbritebi\nbritei\nbroadway\nbubble\nbubble__\nbubble_b\nbulbhead\nc1______\nc2______\nc_ascii_\nc_consen\ncalgphy2\ncaligraphy\ncatwalk\ncaus_in_\nchar1___\nchar2___\nchar3___\nchar4___\ncharact1\ncharact2\ncharact3\ncharact4\ncharact5\ncharact6\ncharacte\ncharset_\nchartr\nchartri\nchunky\nclb6x10\nclb8x10\nclb8x8\ncli8x8\nclr4x6\nclr5x10\nclr5x6\nclr5x8\nclr6x10\nclr6x6\nclr6x8\nclr7x10\nclr7x8\nclr8x10\nclr8x8\ncoil_cop\ncoinstak\ncolossal\ncom_sen_\ncomputer\ncontessa\ncontrast\nconvoy__\ncosmic\ncosmike\ncour\ncourb\ncourbi\ncouri\ncrawford\ncricket\ncursive\ncyberlarge\ncybermedium\ncybersmall\nd_dragon\ndcs_bfmo\ndecimal\ndeep_str\ndefleppard\ndemo_1__\ndemo_2__\ndemo_m__\ndevilish\ndiamond\ndigital\ndoh\ndoom\ndotmatrix\ndouble\ndrpepper\ndruid___\ndwhistled\ne__fist_\nebbs_1__\nebbs_2__\neca_____\neftichess\neftifont\neftipiti\neftirobot\neftitalic\neftiwall\neftiwater\nepic\netcrvs__\nf15_____\nfaces_of\nfair_mea\nfairligh\nfantasy_\nfbr12___\nfbr1____\nfbr2____\nfbr_stri\nfbr_tilt\nfender\nfinalass\nfireing_\nflyn_sh\nfourtops\nfp1_____\nfp2_____\nfraktur\nfunky_dr\nfuture_1\nfuture_2\nfuture_3\nfuture_4\nfuture_5\nfuture_6\nfuture_7\nfuture_8\nfuzzy\ngauntlet\nghost_bo\ngoofy\ngothic\ngothic__\ngraceful\ngradient\ngraffiti\ngrand_pr\ngreek\ngreen_be\nhades___\nheavy_me\nhelv\nhelvb\nhelvbi\nhelvi\nheroboti\nhex\nhigh_noo\nhills___\nhollywood\nhome_pak\nhouse_of\nhypa_bal\nhyper___\ninc_raw_\ninvita\nisometric1\nisometric2\nisometric3\nisometric4\nitalic\nitalics_\nivrit\njazmine\njerusalem\njoust___\nkatakana\nkban\nkgames_i\nkik_star\nkrak_out\nlarry3d\nlazy_jon\nlcd\nlean\nletter_w\nletters\nletterw3\nlexible_\nlinux\nlockergnome\nmad_nurs\nmadrid\nmagic_ma\nmarquee\nmaster_o\nmaxfour\nmayhem_d\nmcg_____\nmig_ally\nmike\nmini\nmirror\nmnemonic\nmodern__\nmorse\nmoscow\nmshebrew210\nnancyj\nnancyj-fancy\nnancyj-underlined\nnew_asci\nnfi1____\nnipples\nnotie_ca\nnpn_____\nntgreek\nnvscript\no8\noctal\nodel_lak\nogre\nok_beer_\nos2\noutrun__\np_s_h_m_\np_skateb\npacos_pe\npanther_\npawn_ins\npawp\npeaks\npebbles\npepper\nphonix__\nplatoon2\nplatoon_\npod_____\npoison\npuffy\npyramid\nr2-d2___\nrad_____\nrad_phan\nradical_\nrainbow_\nrally_s2\nrally_sp\nrampage_\nrastan__\nraw_recu\nrci_____\nrectangles\nrelief\nrelief2\nrev\nripper!_\nroad_rai\nrockbox_\nrok_____\nroman\nroman___\nrot13\nrounded\nrowancap\nrozzo\nrunic\nrunyc\nsans\nsansb\nsansbi\nsansi\nsblood\nsbook\nsbookb\nsbookbi\nsbooki\nscript\nscript__\nserifcap\nshadow\nshimrod\nshort\nskate_ro\nskateord\nskateroc\nsketch_s\nslant\nslide\nslscript\nsm______\nsmall\nsmisome1\nsmkeyboard\nsmscript\nsmshadow\nsmslant\nsmtengwar\nspace_op\nspc_demo\nspeed\nstacey\nstampatello\nstandard\nstar_war\nstarwars\nstealth_\nstellar\nstencil1\nstencil2\nstop\nstraight\nstreet_s\nsubteran\nsuper_te\nt__of_ap\ntanja\ntav1____\ntaxi____\ntec1____\ntec_7000\ntecrvs__\ntengwar\nterm\nthick\nthin\nthreepoint\nti_pan__\nticks\nticksslant\ntiles\ntimes\ntimesofl\ntinker-toy\ntomahawk\ntombstone\ntop_duck\ntrashman\ntrek\ntriad_st\nts1_____\ntsalagi\ntsm_____\ntsn_base\ntty\nttyb\ntubular\ntwin_cob\ntwopoint\ntype_set\nucf_fan_\nugalympi\nunarmed_\nunivers\nusa_____\nusa_pq__\nusaflag\nutopia\nutopiab\nutopiabi\nutopiai\nvortron_\nwar_of_w\nwavy\nweird\nwhimsy\nxbrite\nxbriteb\nxbritebi\nxbritei\nxchartr\nxchartri\nxcour\nxcourb\nxcourbi\nxcouri\nxhelv\nxhelvb\nxhelvbi\nxhelvi\nxsans\nxsansb\nxsansbi\nxsansi\nxsbook\nxsbookb\nxsbookbi\nxsbooki\nxtimes\nxtty\nxttyb\nyie-ar__\nyie_ar_k\nz-pilot_\nzig_zag_\nzone7___\n```\n\n## License\n\nMIT\n\n**Free Software, Hell Yeah!**\n\n## Author\n\n[Deepak Patidar](https://github.com/DeepakDarkiee/great-text)\n',
    'author': 'Deepak Patidar',
    'author_email': 'info.deepakpatidar@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/DeepakDarkiee/great-text.git',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6.0',
}


setup(**setup_kwargs)
