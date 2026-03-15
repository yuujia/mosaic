## Header
mosaic_anchor: ACTIVE_MANIFEST
mosaic_project: Mosaic
mosaic_schema_version: 1
generated_on: 2026-03-10
source_file: 00_config/active_portfolio.xlsx
source_of_truth: 00_config/active_portfolio.xlsx

## Agent Entry Points
Primary workflow entry point for Mosaic agents.

Steps:
1. Open this file (active_manifest.md).
2. Find the requested bucket section under "## Buckets".
3. Open the listed bucket_thesis_file.
4. Open each company_file listed in the bucket.
5. Apply extraction/scanning rules defined in: agents/skills/analyst.md

Notes:
- Agents must not assume directory listing is available; they should use manifest paths.

## Conventions
- Paths are relative to the Mosaic root.
- Bucket thesis convention: `buckets/<BUCKET_ID>/<BUCKET_ID>_bucket_thesis.md`
- Company file convention: `buckets/<BUCKET_ID>/<TICKER>/<TICKER>.md`
- Buckets are sorted A->Z and tickers are sorted A->Z.

## Buckets


<!-- BEGIN AUTO:BUCKETS -->
### AGENTICS
- bucket_id: `AGENTICS`
- bucket_symbol: `.AGENTICS`
- bucket_path: `buckets/AGENTICS/`
- bucket_thesis_file: `buckets/AGENTICS/AGENTICS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AMPL | Short | buckets/AGENTICS/AMPL/AMPL.md |
| AVPT | Short | buckets/AGENTICS/AVPT/AVPT.md |
| BILL | Short | buckets/AGENTICS/BILL/BILL.md |
| CWAN | Short | buckets/AGENTICS/CWAN/CWAN.md |
| DOCU | Short | buckets/AGENTICS/DOCU/DOCU.md |
| FIVN | Short | buckets/AGENTICS/FIVN/FIVN.md |
| FRSH | Short | buckets/AGENTICS/FRSH/FRSH.md |
| GDDY | Short | buckets/AGENTICS/GDDY/GDDY.md |
| INTA | Short | buckets/AGENTICS/INTA/INTA.md |
| INTU | Short | buckets/AGENTICS/INTU/INTU.md |
| LAW | Short | buckets/AGENTICS/LAW/LAW.md |
| OTEX | Short | buckets/AGENTICS/OTEX/OTEX.md |
| PAY | Short | buckets/AGENTICS/PAY/PAY.md |
| QLYS | Short | buckets/AGENTICS/QLYS/QLYS.md |
| RPD | Short | buckets/AGENTICS/RPD/RPD.md |
| SPSC | Short | buckets/AGENTICS/SPSC/SPSC.md |
| TENB | Short | buckets/AGENTICS/TENB/TENB.md |
| TYL | Short | buckets/AGENTICS/TYL/TYL.md |
| VRNS | Short | buckets/AGENTICS/VRNS/VRNS.md |
| WIX | Short | buckets/AGENTICS/WIX/WIX.md |
| WK | Short | buckets/AGENTICS/WK/WK.md |
| ZIP | Short | buckets/AGENTICS/ZIP/ZIP.md |

### AIOUT
- bucket_id: `AIOUT`
- bucket_symbol: `.AIOUT`
- bucket_path: `buckets/AIOUT/`
- bucket_thesis_file: `buckets/AIOUT/AIOUT_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| ACN | Short | buckets/AIOUT/ACN/ACN.md |
| CNXC | Short | buckets/AIOUT/CNXC/CNXC.md |
| CTSH | Short | buckets/AIOUT/CTSH/CTSH.md |
| DXC | Short | buckets/AIOUT/DXC/DXC.md |
| EPAM | Short | buckets/AIOUT/EPAM/EPAM.md |
| EXLS | Short | buckets/AIOUT/EXLS/EXLS.md |
| FVRR | Short | buckets/AIOUT/FVRR/FVRR.md |
| G | Short | buckets/AIOUT/G/G.md |
| GLOB | Short | buckets/AIOUT/GLOB/GLOB.md |
| HRB | Short | buckets/AIOUT/HRB/HRB.md |
| INFY | Short | buckets/AIOUT/INFY/INFY.md |
| KFRC | Short | buckets/AIOUT/KFRC/KFRC.md |
| KFY | Short | buckets/AIOUT/KFY/KFY.md |
| MAN | Short | buckets/AIOUT/MAN/MAN.md |
| OMC | Short | buckets/AIOUT/OMC/OMC.md |
| RHI | Short | buckets/AIOUT/RHI/RHI.md |
| TASK | Short | buckets/AIOUT/TASK/TASK.md |
| TTEC | Short | buckets/AIOUT/TTEC/TTEC.md |
| UPWK | Short | buckets/AIOUT/UPWK/UPWK.md |
| WPP | Short | buckets/AIOUT/WPP/WPP.md |

### BUILD
- bucket_id: `BUILD`
- bucket_symbol: `.BUILD`
- bucket_path: `buckets/BUILD/`
- bucket_thesis_file: `buckets/BUILD/BUILD_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BLD | Long | buckets/BUILD/BLD/BLD.md |
| BLDR | Long | buckets/BUILD/BLDR/BLDR.md |
| FERG | Long | buckets/BUILD/FERG/FERG.md |
| QXO | Long | buckets/BUILD/QXO/QXO.md |
| WSO | Long | buckets/BUILD/WSO/WSO.md |

### CANCER
- bucket_id: `CANCER`
- bucket_symbol: `.CANCER`
- bucket_path: `buckets/CANCER/`
- bucket_thesis_file: `buckets/CANCER/CANCER_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| ADPT | Long | buckets/CANCER/ADPT/ADPT.md |
| GH | Long | buckets/CANCER/GH/GH.md |
| NEO | Long | buckets/CANCER/NEO/NEO.md |
| NTRA | Long | buckets/CANCER/NTRA/NTRA.md |
| TEM | Long | buckets/CANCER/TEM/TEM.md |
| VCYT | Long | buckets/CANCER/VCYT/VCYT.md |

### Cash
- bucket_id: `Cash`
- bucket_symbol: `Cash`
- bucket_path: `buckets/Cash/`
- bucket_thesis_file: `buckets/Cash/Cash_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| FOPXX | Long | buckets/Cash/FOPXX/FOPXX.md |

### CASINO
- bucket_id: `CASINO`
- bucket_symbol: `.CASINO`
- bucket_path: `buckets/CASINO/`
- bucket_thesis_file: `buckets/CASINO/CASINO_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BYD | Short | buckets/CASINO/BYD/BYD.md |
| CZR | Short | buckets/CASINO/CZR/CZR.md |
| PENN | Short | buckets/CASINO/PENN/PENN.md |
| RRR | Short | buckets/CASINO/RRR/RRR.md |

### CHINAS
- bucket_id: `CHINAS`
- bucket_symbol: `.CHINAS`
- bucket_path: `buckets/CHINAS/`
- bucket_thesis_file: `buckets/CHINAS/CHINAS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| CBT | Short | buckets/CHINAS/CBT/CBT.md |
| CC | Short | buckets/CHINAS/CC/CC.md |
| CE | Short | buckets/CHINAS/CE/CE.md |
| DOW | Short | buckets/CHINAS/DOW/DOW.md |
| EMN | Short | buckets/CHINAS/EMN/EMN.md |
| HUN | Short | buckets/CHINAS/HUN/HUN.md |
| KRO | Short | buckets/CHINAS/KRO/KRO.md |
| LYB | Short | buckets/CHINAS/LYB/LYB.md |
| MGA | Short | buckets/CHINAS/MGA/MGA.md |
| STLA | Short | buckets/CHINAS/STLA/STLA.md |
| TROX | Short | buckets/CHINAS/TROX/TROX.md |
| TSLA | Short | buckets/CHINAS/TSLA/TSLA.md |

### CRYPTO
- bucket_id: `CRYPTO`
- bucket_symbol: `.CRYPTO`
- bucket_path: `buckets/CRYPTO/`
- bucket_thesis_file: `buckets/CRYPTO/CRYPTO_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| CBOE | Long | buckets/CRYPTO/CBOE/CBOE.md |
| CME | Long | buckets/CRYPTO/CME/CME.md |
| COIN | Long | buckets/CRYPTO/COIN/COIN.md |
| HOOD | Long | buckets/CRYPTO/HOOD/HOOD.md |
| STT | Long | buckets/CRYPTO/STT/STT.md |
| VIRT | Long | buckets/CRYPTO/VIRT/VIRT.md |

### DATASRVS
- bucket_id: `DATASRVS`
- bucket_symbol: `.DATASRVS`
- bucket_path: `buckets/DATASRVS/`
- bucket_thesis_file: `buckets/DATASRVS/DATASRVS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| CLVT | Short | buckets/DATASRVS/CLVT/CLVT.md |
| FDS | Short | buckets/DATASRVS/FDS/FDS.md |
| FICO | Short | buckets/DATASRVS/FICO/FICO.md |
| FORR | Short | buckets/DATASRVS/FORR/FORR.md |
| GTM | Short | buckets/DATASRVS/GTM/GTM.md |
| IT | Short | buckets/DATASRVS/IT/IT.md |
| MCO | Short | buckets/DATASRVS/MCO/MCO.md |
| MORN | Short | buckets/DATASRVS/MORN/MORN.md |
| MSCI | Short | buckets/DATASRVS/MSCI/MSCI.md |
| RELX | Short | buckets/DATASRVS/RELX/RELX.md |
| SPGI | Short | buckets/DATASRVS/SPGI/SPGI.md |
| TRI | Short | buckets/DATASRVS/TRI/TRI.md |
| VERX | Short | buckets/DATASRVS/VERX/VERX.md |
| WTKWY | Short | buckets/DATASRVS/WTKWY/WTKWY.md |

### DCSHORTS
- bucket_id: `DCSHORTS`
- bucket_symbol: `.DCSHORTS`
- bucket_path: `buckets/DCSHORTS/`
- bucket_thesis_file: `buckets/DCSHORTS/DCSHORTS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| APLD | Short | buckets/DCSHORTS/APLD/APLD.md |
| CEG | Short | buckets/DCSHORTS/CEG/CEG.md |
| CIFR | Short | buckets/DCSHORTS/CIFR/CIFR.md |
| CORZ | Short | buckets/DCSHORTS/CORZ/CORZ.md |
| CRWV | Short | buckets/DCSHORTS/CRWV/CRWV.md |
| DLR | Short | buckets/DCSHORTS/DLR/DLR.md |
| HUT | Short | buckets/DCSHORTS/HUT/HUT.md |
| IREN | Short | buckets/DCSHORTS/IREN/IREN.md |
| NBIS | Short | buckets/DCSHORTS/NBIS/NBIS.md |
| NRG | Short | buckets/DCSHORTS/NRG/NRG.md |
| TLN | Short | buckets/DCSHORTS/TLN/TLN.md |
| VST | Short | buckets/DCSHORTS/VST/VST.md |
| WULF | Short | buckets/DCSHORTS/WULF/WULF.md |

### DRIVE
- bucket_id: `DRIVE`
- bucket_symbol: `.DRIVE`
- bucket_path: `buckets/DRIVE/`
- bucket_thesis_file: `buckets/DRIVE/DRIVE_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AZO | Long | buckets/DRIVE/AZO/AZO.md |
| CASY | Long | buckets/DRIVE/CASY/CASY.md |
| MUSA | Long | buckets/DRIVE/MUSA/MUSA.md |
| ORLY | Long | buckets/DRIVE/ORLY/ORLY.md |
| VVV | Long | buckets/DRIVE/VVV/VVV.md |

### DTECH
- bucket_id: `DTECH`
- bucket_symbol: `.DTECH`
- bucket_path: `buckets/DTECH/`
- bucket_thesis_file: `buckets/DTECH/DTECH_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AVAV | Long | buckets/DTECH/AVAV/AVAV.md |
| KRMN | Long | buckets/DTECH/KRMN/KRMN.md |
| KTOS | Long | buckets/DTECH/KTOS/KTOS.md |
| LHX | Long | buckets/DTECH/LHX/LHX.md |
| MRCY | Long | buckets/DTECH/MRCY/MRCY.md |

### ECOMM
- bucket_id: `ECOMM`
- bucket_symbol: `.ECOMM`
- bucket_path: `buckets/ECOMM/`
- bucket_thesis_file: `buckets/ECOMM/ECOMM_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BKNG | Short | buckets/ECOMM/BKNG/BKNG.md |
| BRZE | Short | buckets/ECOMM/BRZE/BRZE.md |
| DOCN | Short | buckets/ECOMM/DOCN/DOCN.md |
| EXPE | Short | buckets/ECOMM/EXPE/EXPE.md |
| HUBS | Short | buckets/ECOMM/HUBS/HUBS.md |
| KVYO | Short | buckets/ECOMM/KVYO/KVYO.md |
| SPT | Short | buckets/ECOMM/SPT/SPT.md |
| TRIP | Short | buckets/ECOMM/TRIP/TRIP.md |

### HCSUP
- bucket_id: `HCSUP`
- bucket_symbol: `.HCSUP`
- bucket_path: `buckets/HCSUP/`
- bucket_thesis_file: `buckets/HCSUP/HCSUP_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| ACH | Short | buckets/HCSUP/ACH/ACH.md |
| BAX | Short | buckets/HCSUP/BAX/BAX.md |
| BDX | Short | buckets/HCSUP/BDX/BDX.md |
| ELAN | Short | buckets/HCSUP/ELAN/ELAN.md |
| HCA | Short | buckets/HCSUP/HCA/HCA.md |
| HSIC | Short | buckets/HCSUP/HSIC/HSIC.md |
| ICUI | Short | buckets/HCSUP/ICUI/ICUI.md |
| IDXX | Short | buckets/HCSUP/IDXX/IDXX.md |
| SGRY | Short | buckets/HCSUP/SGRY/SGRY.md |
| TFX | Short | buckets/HCSUP/TFX/TFX.md |
| THC | Short | buckets/HCSUP/THC/THC.md |
| UHS | Short | buckets/HCSUP/UHS/UHS.md |
| WAT | Short | buckets/HCSUP/WAT/WAT.md |
| ZTS | Short | buckets/HCSUP/ZTS/ZTS.md |

### HOTEL
- bucket_id: `HOTEL`
- bucket_symbol: `.HOTEL`
- bucket_path: `buckets/HOTEL/`
- bucket_thesis_file: `buckets/HOTEL/HOTEL_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| APLE | Short | buckets/HOTEL/APLE/APLE.md |
| DRH | Short | buckets/HOTEL/DRH/DRH.md |
| HST | Short | buckets/HOTEL/HST/HST.md |
| PEB | Short | buckets/HOTEL/PEB/PEB.md |
| PK | Short | buckets/HOTEL/PK/PK.md |
| RHP | Short | buckets/HOTEL/RHP/RHP.md |
| RLJ | Short | buckets/HOTEL/RLJ/RLJ.md |
| SHO | Short | buckets/HOTEL/SHO/SHO.md |
| XHR | Short | buckets/HOTEL/XHR/XHR.md |

### Index
- bucket_id: `Index`
- bucket_symbol: `Index`
- bucket_path: `buckets/Index/`
- bucket_thesis_file: `buckets/Index/Index_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| RSP | Short | buckets/Index/RSP/RSP.md |

### INDOPS
- bucket_id: `INDOPS`
- bucket_symbol: `.INDOPS`
- bucket_path: `buckets/INDOPS/`
- bucket_thesis_file: `buckets/INDOPS/INDOPS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AIT | Long | buckets/INDOPS/AIT/AIT.md |
| AME | Long | buckets/INDOPS/AME/AME.md |
| DXPE | Long | buckets/INDOPS/DXPE/DXPE.md |
| EMR | Long | buckets/INDOPS/EMR/EMR.md |
| FTV | Long | buckets/INDOPS/FTV/FTV.md |
| TT | Long | buckets/INDOPS/TT/TT.md |

### INF
- bucket_id: `INF`
- bucket_symbol: `.INF`
- bucket_path: `buckets/INF/`
- bucket_thesis_file: `buckets/INF/INF_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| CNM | Long | buckets/INF/CNM/CNM.md |
| MTZ | Long | buckets/INF/MTZ/MTZ.md |
| MYRG | Long | buckets/INF/MYRG/MYRG.md |
| PWR | Long | buckets/INF/PWR/PWR.md |
| ROAD | Long | buckets/INF/ROAD/ROAD.md |

### LAW
- bucket_id: `LAW`
- bucket_symbol: `.LAW`
- bucket_path: `buckets/LAW/`
- bucket_thesis_file: `buckets/LAW/LAW_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AXON | Long | buckets/LAW/AXON/AXON.md |
| CDRE | Long | buckets/LAW/CDRE/CDRE.md |
| CLBT | Long | buckets/LAW/CLBT/CLBT.md |
| MSI | Long | buckets/LAW/MSI/MSI.md |

### MAHA
- bucket_id: `MAHA`
- bucket_symbol: `.MAHA`
- bucket_path: `buckets/MAHA/`
- bucket_thesis_file: `buckets/MAHA/MAHA_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BF_B | Short | buckets/MAHA/BF_B/BF_B.md |
| CPB | Short | buckets/MAHA/CPB/CPB.md |
| DEO | Short | buckets/MAHA/DEO/DEO.md |
| FLO | Short | buckets/MAHA/FLO/FLO.md |
| GIS | Short | buckets/MAHA/GIS/GIS.md |
| JJSF | Short | buckets/MAHA/JJSF/JJSF.md |
| KHC | Short | buckets/MAHA/KHC/KHC.md |
| MDLZ | Short | buckets/MAHA/MDLZ/MDLZ.md |
| POST | Short | buckets/MAHA/POST/POST.md |
| SAM | Short | buckets/MAHA/SAM/SAM.md |
| SJM | Short | buckets/MAHA/SJM/SJM.md |
| STZ | Short | buckets/MAHA/STZ/STZ.md |
| TAP | Short | buckets/MAHA/TAP/TAP.md |

### MDAS
- bucket_id: `MDAS`
- bucket_symbol: `.MDAS`
- bucket_path: `buckets/MDAS/`
- bucket_thesis_file: `buckets/MDAS/MDAS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AMCX | Short | buckets/MDAS/AMCX/AMCX.md |
| ANGI | Short | buckets/MDAS/ANGI/ANGI.md |
| COUR | Short | buckets/MDAS/COUR/COUR.md |
| GRPN | Short | buckets/MDAS/GRPN/GRPN.md |
| IAC | Short | buckets/MDAS/IAC/IAC.md |
| IHRT | Short | buckets/MDAS/IHRT/IHRT.md |
| LION | Short | buckets/MDAS/LION/LION.md |
| PINS | Short | buckets/MDAS/PINS/PINS.md |
| PTON | Short | buckets/MDAS/PTON/PTON.md |
| RBLX | Short | buckets/MDAS/RBLX/RBLX.md |
| ROKU | Short | buckets/MDAS/ROKU/ROKU.md |
| SIRI | Short | buckets/MDAS/SIRI/SIRI.md |
| SSTK | Short | buckets/MDAS/SSTK/SSTK.md |
| STRZ | Short | buckets/MDAS/STRZ/STRZ.md |
| YELP | Short | buckets/MDAS/YELP/YELP.md |
| ZD | Short | buckets/MDAS/ZD/ZD.md |

### MTECH
- bucket_id: `MTECH`
- bucket_symbol: `.MTECH`
- bucket_path: `buckets/MTECH/`
- bucket_thesis_file: `buckets/MTECH/MTECH_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| COMP | Long | buckets/MTECH/COMP/COMP.md |
| PFSI | Long | buckets/MTECH/PFSI/PFSI.md |
| RKT | Long | buckets/MTECH/RKT/RKT.md |
| UWMC | Long | buckets/MTECH/UWMC/UWMC.md |
| Z | Long | buckets/MTECH/Z/Z.md |

### POWR
- bucket_id: `POWR`
- bucket_symbol: `.POWR`
- bucket_path: `buckets/POWR/`
- bucket_thesis_file: `buckets/POWR/POWR_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| AEE | Long | buckets/POWR/AEE/AEE.md |
| AEP | Long | buckets/POWR/AEP/AEP.md |
| ETR | Long | buckets/POWR/ETR/ETR.md |
| NI | Long | buckets/POWR/NI/NI.md |
| OGE | Long | buckets/POWR/OGE/OGE.md |

### PRIVATE
- bucket_id: `PRIVATE`
- bucket_symbol: `.PRIVATE`
- bucket_path: `buckets/PRIVATE/`
- bucket_thesis_file: `buckets/PRIVATE/PRIVATE_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| APO | Short | buckets/PRIVATE/APO/APO.md |
| ARES | Short | buckets/PRIVATE/ARES/ARES.md |
| BX | Short | buckets/PRIVATE/BX/BX.md |
| CG | Short | buckets/PRIVATE/CG/CG.md |
| KKR | Short | buckets/PRIVATE/KKR/KKR.md |
| OWL | Short | buckets/PRIVATE/OWL/OWL.md |
| TPG | Short | buckets/PRIVATE/TPG/TPG.md |

### REST
- bucket_id: `REST`
- bucket_symbol: `.REST`
- bucket_path: `buckets/REST/`
- bucket_thesis_file: `buckets/REST/REST_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BJRI | Short | buckets/REST/BJRI/BJRI.md |
| BLMN | Short | buckets/REST/BLMN/BLMN.md |
| BROS | Short | buckets/REST/BROS/BROS.md |
| CAKE | Short | buckets/REST/CAKE/CAKE.md |
| CAVA | Short | buckets/REST/CAVA/CAVA.md |
| CBRL | Short | buckets/REST/CBRL/CBRL.md |
| CMG | Short | buckets/REST/CMG/CMG.md |
| DRI | Short | buckets/REST/DRI/DRI.md |
| EAT | Short | buckets/REST/EAT/EAT.md |
| FWRG | Short | buckets/REST/FWRG/FWRG.md |
| SG | Short | buckets/REST/SG/SG.md |
| TXRH | Short | buckets/REST/TXRH/TXRH.md |

### STABLE
- bucket_id: `STABLE`
- bucket_symbol: `.STABLE`
- bucket_path: `buckets/STABLE/`
- bucket_thesis_file: `buckets/STABLE/STABLE_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| MQ | Short | buckets/STABLE/MQ/MQ.md |

### STABLECO
- bucket_id: `STABLECO`
- bucket_symbol: `.STABLECO`
- bucket_path: `buckets/STABLECO/`
- bucket_thesis_file: `buckets/STABLECO/STABLECO_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| ADYEY | Short | buckets/STABLECO/ADYEY/ADYEY.md |
| EEFT | Short | buckets/STABLECO/EEFT/EEFT.md |
| FISV | Short | buckets/STABLECO/FISV/FISV.md |
| GPN | Short | buckets/STABLECO/GPN/GPN.md |
| MA | Short | buckets/STABLECO/MA/MA.md |
| PYPL | Short | buckets/STABLECO/PYPL/PYPL.md |
| V | Short | buckets/STABLECO/V/V.md |
| WU | Short | buckets/STABLECO/WU/WU.md |
| XYZ | Short | buckets/STABLECO/XYZ/XYZ.md |

### TESTS
- bucket_id: `TESTS`
- bucket_symbol: `.TESTS`
- bucket_path: `buckets/TESTS/`
- bucket_thesis_file: `buckets/TESTS/TESTS_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| BIO | Long | buckets/TESTS/BIO/BIO.md |
| DGX | Long | buckets/TESTS/DGX/DGX.md |
| LH | Long | buckets/TESTS/LH/LH.md |
| QGEN | Long | buckets/TESTS/QGEN/QGEN.md |
| RVTY | Long | buckets/TESTS/RVTY/RVTY.md |
| TECH | Long | buckets/TESTS/TECH/TECH.md |

### TRANSPOR
- bucket_id: `TRANSPOR`
- bucket_symbol: `.TRANSPOR`
- bucket_path: `buckets/TRANSPOR/`
- bucket_thesis_file: `buckets/TRANSPOR/TRANSPOR_bucket_thesis.md`

| ticker | side | company_file |
|---|---|---|
| ARCB | Long | buckets/TRANSPOR/ARCB/ARCB.md |
| CP | Long | buckets/TRANSPOR/CP/CP.md |
| CSX | Long | buckets/TRANSPOR/CSX/CSX.md |
| ODFL | Long | buckets/TRANSPOR/ODFL/ODFL.md |
| SAIA | Long | buckets/TRANSPOR/SAIA/SAIA.md |
| XPO | Long | buckets/TRANSPOR/XPO/XPO.md |
<!-- END AUTO:BUCKETS -->
## Global Company Index
<!-- BEGIN AUTO:GLOBAL_COMPANY_INDEX -->
| ticker | company_file | bucket_id |
|---|---|---|
| ACH | buckets/HCSUP/ACH/ACH.md | HCSUP |
| ACN | buckets/AIOUT/ACN/ACN.md | AIOUT |
| ADPT | buckets/CANCER/ADPT/ADPT.md | CANCER |
| ADYEY | buckets/STABLECO/ADYEY/ADYEY.md | STABLECO |
| AEE | buckets/POWR/AEE/AEE.md | POWR |
| AEP | buckets/POWR/AEP/AEP.md | POWR |
| AIT | buckets/INDOPS/AIT/AIT.md | INDOPS |
| AMCX | buckets/MDAS/AMCX/AMCX.md | MDAS |
| AME | buckets/INDOPS/AME/AME.md | INDOPS |
| AMPL | buckets/AGENTICS/AMPL/AMPL.md | AGENTICS |
| ANGI | buckets/MDAS/ANGI/ANGI.md | MDAS |
| APLD | buckets/DCSHORTS/APLD/APLD.md | DCSHORTS |
| APLE | buckets/HOTEL/APLE/APLE.md | HOTEL |
| APO | buckets/PRIVATE/APO/APO.md | PRIVATE |
| ARCB | buckets/TRANSPOR/ARCB/ARCB.md | TRANSPOR |
| ARES | buckets/PRIVATE/ARES/ARES.md | PRIVATE |
| AVAV | buckets/DTECH/AVAV/AVAV.md | DTECH |
| AVPT | buckets/AGENTICS/AVPT/AVPT.md | AGENTICS |
| AXON | buckets/LAW/AXON/AXON.md | LAW |
| AZO | buckets/DRIVE/AZO/AZO.md | DRIVE |
| BAX | buckets/HCSUP/BAX/BAX.md | HCSUP |
| BDX | buckets/HCSUP/BDX/BDX.md | HCSUP |
| BF_B | buckets/MAHA/BF_B/BF_B.md | MAHA |
| BILL | buckets/AGENTICS/BILL/BILL.md | AGENTICS |
| BIO | buckets/TESTS/BIO/BIO.md | TESTS |
| BJRI | buckets/REST/BJRI/BJRI.md | REST |
| BKNG | buckets/ECOMM/BKNG/BKNG.md | ECOMM |
| BLD | buckets/BUILD/BLD/BLD.md | BUILD |
| BLDR | buckets/BUILD/BLDR/BLDR.md | BUILD |
| BLMN | buckets/REST/BLMN/BLMN.md | REST |
| BROS | buckets/REST/BROS/BROS.md | REST |
| BRZE | buckets/ECOMM/BRZE/BRZE.md | ECOMM |
| BX | buckets/PRIVATE/BX/BX.md | PRIVATE |
| BYD | buckets/CASINO/BYD/BYD.md | CASINO |
| CAKE | buckets/REST/CAKE/CAKE.md | REST |
| CASY | buckets/DRIVE/CASY/CASY.md | DRIVE |
| CAVA | buckets/REST/CAVA/CAVA.md | REST |
| CBOE | buckets/CRYPTO/CBOE/CBOE.md | CRYPTO |
| CBRL | buckets/REST/CBRL/CBRL.md | REST |
| CBT | buckets/CHINAS/CBT/CBT.md | CHINAS |
| CC | buckets/CHINAS/CC/CC.md | CHINAS |
| CDRE | buckets/LAW/CDRE/CDRE.md | LAW |
| CE | buckets/CHINAS/CE/CE.md | CHINAS |
| CEG | buckets/DCSHORTS/CEG/CEG.md | DCSHORTS |
| CG | buckets/PRIVATE/CG/CG.md | PRIVATE |
| CIFR | buckets/DCSHORTS/CIFR/CIFR.md | DCSHORTS |
| CLBT | buckets/LAW/CLBT/CLBT.md | LAW |
| CLVT | buckets/DATASRVS/CLVT/CLVT.md | DATASRVS |
| CME | buckets/CRYPTO/CME/CME.md | CRYPTO |
| CMG | buckets/REST/CMG/CMG.md | REST |
| CNM | buckets/INF/CNM/CNM.md | INF |
| CNXC | buckets/AIOUT/CNXC/CNXC.md | AIOUT |
| COIN | buckets/CRYPTO/COIN/COIN.md | CRYPTO |
| COMP | buckets/MTECH/COMP/COMP.md | MTECH |
| CORZ | buckets/DCSHORTS/CORZ/CORZ.md | DCSHORTS |
| COUR | buckets/MDAS/COUR/COUR.md | MDAS |
| CP | buckets/TRANSPOR/CP/CP.md | TRANSPOR |
| CPB | buckets/MAHA/CPB/CPB.md | MAHA |
| CRWV | buckets/DCSHORTS/CRWV/CRWV.md | DCSHORTS |
| CSX | buckets/TRANSPOR/CSX/CSX.md | TRANSPOR |
| CTSH | buckets/AIOUT/CTSH/CTSH.md | AIOUT |
| CWAN | buckets/AGENTICS/CWAN/CWAN.md | AGENTICS |
| CZR | buckets/CASINO/CZR/CZR.md | CASINO |
| DEO | buckets/MAHA/DEO/DEO.md | MAHA |
| DGX | buckets/TESTS/DGX/DGX.md | TESTS |
| DLR | buckets/DCSHORTS/DLR/DLR.md | DCSHORTS |
| DOCN | buckets/ECOMM/DOCN/DOCN.md | ECOMM |
| DOCU | buckets/AGENTICS/DOCU/DOCU.md | AGENTICS |
| DOW | buckets/CHINAS/DOW/DOW.md | CHINAS |
| DRH | buckets/HOTEL/DRH/DRH.md | HOTEL |
| DRI | buckets/REST/DRI/DRI.md | REST |
| DXC | buckets/AIOUT/DXC/DXC.md | AIOUT |
| DXPE | buckets/INDOPS/DXPE/DXPE.md | INDOPS |
| EAT | buckets/REST/EAT/EAT.md | REST |
| EEFT | buckets/STABLECO/EEFT/EEFT.md | STABLECO |
| ELAN | buckets/HCSUP/ELAN/ELAN.md | HCSUP |
| EMN | buckets/CHINAS/EMN/EMN.md | CHINAS |
| EMR | buckets/INDOPS/EMR/EMR.md | INDOPS |
| EPAM | buckets/AIOUT/EPAM/EPAM.md | AIOUT |
| ETR | buckets/POWR/ETR/ETR.md | POWR |
| EXLS | buckets/AIOUT/EXLS/EXLS.md | AIOUT |
| EXPE | buckets/ECOMM/EXPE/EXPE.md | ECOMM |
| FDS | buckets/DATASRVS/FDS/FDS.md | DATASRVS |
| FERG | buckets/BUILD/FERG/FERG.md | BUILD |
| FICO | buckets/DATASRVS/FICO/FICO.md | DATASRVS |
| FISV | buckets/STABLECO/FISV/FISV.md | STABLECO |
| FIVN | buckets/AGENTICS/FIVN/FIVN.md | AGENTICS |
| FLO | buckets/MAHA/FLO/FLO.md | MAHA |
| FOPXX | buckets/Cash/FOPXX/FOPXX.md | Cash |
| FORR | buckets/DATASRVS/FORR/FORR.md | DATASRVS |
| FRSH | buckets/AGENTICS/FRSH/FRSH.md | AGENTICS |
| FTV | buckets/INDOPS/FTV/FTV.md | INDOPS |
| FVRR | buckets/AIOUT/FVRR/FVRR.md | AIOUT |
| FWRG | buckets/REST/FWRG/FWRG.md | REST |
| G | buckets/AIOUT/G/G.md | AIOUT |
| GDDY | buckets/AGENTICS/GDDY/GDDY.md | AGENTICS |
| GH | buckets/CANCER/GH/GH.md | CANCER |
| GIS | buckets/MAHA/GIS/GIS.md | MAHA |
| GLOB | buckets/AIOUT/GLOB/GLOB.md | AIOUT |
| GPN | buckets/STABLECO/GPN/GPN.md | STABLECO |
| GRPN | buckets/MDAS/GRPN/GRPN.md | MDAS |
| GTM | buckets/DATASRVS/GTM/GTM.md | DATASRVS |
| HCA | buckets/HCSUP/HCA/HCA.md | HCSUP |
| HOOD | buckets/CRYPTO/HOOD/HOOD.md | CRYPTO |
| HRB | buckets/AIOUT/HRB/HRB.md | AIOUT |
| HSIC | buckets/HCSUP/HSIC/HSIC.md | HCSUP |
| HST | buckets/HOTEL/HST/HST.md | HOTEL |
| HUBS | buckets/ECOMM/HUBS/HUBS.md | ECOMM |
| HUN | buckets/CHINAS/HUN/HUN.md | CHINAS |
| HUT | buckets/DCSHORTS/HUT/HUT.md | DCSHORTS |
| IAC | buckets/MDAS/IAC/IAC.md | MDAS |
| ICUI | buckets/HCSUP/ICUI/ICUI.md | HCSUP |
| IDXX | buckets/HCSUP/IDXX/IDXX.md | HCSUP |
| IHRT | buckets/MDAS/IHRT/IHRT.md | MDAS |
| INFY | buckets/AIOUT/INFY/INFY.md | AIOUT |
| INTA | buckets/AGENTICS/INTA/INTA.md | AGENTICS |
| INTU | buckets/AGENTICS/INTU/INTU.md | AGENTICS |
| IREN | buckets/DCSHORTS/IREN/IREN.md | DCSHORTS |
| IT | buckets/DATASRVS/IT/IT.md | DATASRVS |
| JJSF | buckets/MAHA/JJSF/JJSF.md | MAHA |
| KFRC | buckets/AIOUT/KFRC/KFRC.md | AIOUT |
| KFY | buckets/AIOUT/KFY/KFY.md | AIOUT |
| KHC | buckets/MAHA/KHC/KHC.md | MAHA |
| KKR | buckets/PRIVATE/KKR/KKR.md | PRIVATE |
| KRMN | buckets/DTECH/KRMN/KRMN.md | DTECH |
| KRO | buckets/CHINAS/KRO/KRO.md | CHINAS |
| KTOS | buckets/DTECH/KTOS/KTOS.md | DTECH |
| KVYO | buckets/ECOMM/KVYO/KVYO.md | ECOMM |
| LAW | buckets/AGENTICS/LAW/LAW.md | AGENTICS |
| LH | buckets/TESTS/LH/LH.md | TESTS |
| LHX | buckets/DTECH/LHX/LHX.md | DTECH |
| LION | buckets/MDAS/LION/LION.md | MDAS |
| LYB | buckets/CHINAS/LYB/LYB.md | CHINAS |
| MA | buckets/STABLECO/MA/MA.md | STABLECO |
| MAN | buckets/AIOUT/MAN/MAN.md | AIOUT |
| MCO | buckets/DATASRVS/MCO/MCO.md | DATASRVS |
| MDLZ | buckets/MAHA/MDLZ/MDLZ.md | MAHA |
| MGA | buckets/CHINAS/MGA/MGA.md | CHINAS |
| MORN | buckets/DATASRVS/MORN/MORN.md | DATASRVS |
| MQ | buckets/STABLE/MQ/MQ.md | STABLE |
| MRCY | buckets/DTECH/MRCY/MRCY.md | DTECH |
| MSCI | buckets/DATASRVS/MSCI/MSCI.md | DATASRVS |
| MSI | buckets/LAW/MSI/MSI.md | LAW |
| MTZ | buckets/INF/MTZ/MTZ.md | INF |
| MUSA | buckets/DRIVE/MUSA/MUSA.md | DRIVE |
| MYRG | buckets/INF/MYRG/MYRG.md | INF |
| NBIS | buckets/DCSHORTS/NBIS/NBIS.md | DCSHORTS |
| NEO | buckets/CANCER/NEO/NEO.md | CANCER |
| NI | buckets/POWR/NI/NI.md | POWR |
| NRG | buckets/DCSHORTS/NRG/NRG.md | DCSHORTS |
| NTRA | buckets/CANCER/NTRA/NTRA.md | CANCER |
| ODFL | buckets/TRANSPOR/ODFL/ODFL.md | TRANSPOR |
| OGE | buckets/POWR/OGE/OGE.md | POWR |
| OMC | buckets/AIOUT/OMC/OMC.md | AIOUT |
| ORLY | buckets/DRIVE/ORLY/ORLY.md | DRIVE |
| OTEX | buckets/AGENTICS/OTEX/OTEX.md | AGENTICS |
| OWL | buckets/PRIVATE/OWL/OWL.md | PRIVATE |
| PAY | buckets/AGENTICS/PAY/PAY.md | AGENTICS |
| PEB | buckets/HOTEL/PEB/PEB.md | HOTEL |
| PENN | buckets/CASINO/PENN/PENN.md | CASINO |
| PFSI | buckets/MTECH/PFSI/PFSI.md | MTECH |
| PINS | buckets/MDAS/PINS/PINS.md | MDAS |
| PK | buckets/HOTEL/PK/PK.md | HOTEL |
| POST | buckets/MAHA/POST/POST.md | MAHA |
| PTON | buckets/MDAS/PTON/PTON.md | MDAS |
| PWR | buckets/INF/PWR/PWR.md | INF |
| PYPL | buckets/STABLECO/PYPL/PYPL.md | STABLECO |
| QGEN | buckets/TESTS/QGEN/QGEN.md | TESTS |
| QLYS | buckets/AGENTICS/QLYS/QLYS.md | AGENTICS |
| QXO | buckets/BUILD/QXO/QXO.md | BUILD |
| RBLX | buckets/MDAS/RBLX/RBLX.md | MDAS |
| RELX | buckets/DATASRVS/RELX/RELX.md | DATASRVS |
| RHI | buckets/AIOUT/RHI/RHI.md | AIOUT |
| RHP | buckets/HOTEL/RHP/RHP.md | HOTEL |
| RKT | buckets/MTECH/RKT/RKT.md | MTECH |
| RLJ | buckets/HOTEL/RLJ/RLJ.md | HOTEL |
| ROAD | buckets/INF/ROAD/ROAD.md | INF |
| ROKU | buckets/MDAS/ROKU/ROKU.md | MDAS |
| RPD | buckets/AGENTICS/RPD/RPD.md | AGENTICS |
| RRR | buckets/CASINO/RRR/RRR.md | CASINO |
| RSP | buckets/Index/RSP/RSP.md | Index |
| RVTY | buckets/TESTS/RVTY/RVTY.md | TESTS |
| SAIA | buckets/TRANSPOR/SAIA/SAIA.md | TRANSPOR |
| SAM | buckets/MAHA/SAM/SAM.md | MAHA |
| SG | buckets/REST/SG/SG.md | REST |
| SGRY | buckets/HCSUP/SGRY/SGRY.md | HCSUP |
| SHO | buckets/HOTEL/SHO/SHO.md | HOTEL |
| SIRI | buckets/MDAS/SIRI/SIRI.md | MDAS |
| SJM | buckets/MAHA/SJM/SJM.md | MAHA |
| SPGI | buckets/DATASRVS/SPGI/SPGI.md | DATASRVS |
| SPSC | buckets/AGENTICS/SPSC/SPSC.md | AGENTICS |
| SPT | buckets/ECOMM/SPT/SPT.md | ECOMM |
| SSTK | buckets/MDAS/SSTK/SSTK.md | MDAS |
| STLA | buckets/CHINAS/STLA/STLA.md | CHINAS |
| STRZ | buckets/MDAS/STRZ/STRZ.md | MDAS |
| STT | buckets/CRYPTO/STT/STT.md | CRYPTO |
| STZ | buckets/MAHA/STZ/STZ.md | MAHA |
| TAP | buckets/MAHA/TAP/TAP.md | MAHA |
| TASK | buckets/AIOUT/TASK/TASK.md | AIOUT |
| TECH | buckets/TESTS/TECH/TECH.md | TESTS |
| TEM | buckets/CANCER/TEM/TEM.md | CANCER |
| TENB | buckets/AGENTICS/TENB/TENB.md | AGENTICS |
| TFX | buckets/HCSUP/TFX/TFX.md | HCSUP |
| THC | buckets/HCSUP/THC/THC.md | HCSUP |
| TLN | buckets/DCSHORTS/TLN/TLN.md | DCSHORTS |
| TPG | buckets/PRIVATE/TPG/TPG.md | PRIVATE |
| TRI | buckets/DATASRVS/TRI/TRI.md | DATASRVS |
| TRIP | buckets/ECOMM/TRIP/TRIP.md | ECOMM |
| TROX | buckets/CHINAS/TROX/TROX.md | CHINAS |
| TSLA | buckets/CHINAS/TSLA/TSLA.md | CHINAS |
| TT | buckets/INDOPS/TT/TT.md | INDOPS |
| TTEC | buckets/AIOUT/TTEC/TTEC.md | AIOUT |
| TXRH | buckets/REST/TXRH/TXRH.md | REST |
| TYL | buckets/AGENTICS/TYL/TYL.md | AGENTICS |
| UHS | buckets/HCSUP/UHS/UHS.md | HCSUP |
| UPWK | buckets/AIOUT/UPWK/UPWK.md | AIOUT |
| UWMC | buckets/MTECH/UWMC/UWMC.md | MTECH |
| V | buckets/STABLECO/V/V.md | STABLECO |
| VCYT | buckets/CANCER/VCYT/VCYT.md | CANCER |
| VERX | buckets/DATASRVS/VERX/VERX.md | DATASRVS |
| VIRT | buckets/CRYPTO/VIRT/VIRT.md | CRYPTO |
| VRNS | buckets/AGENTICS/VRNS/VRNS.md | AGENTICS |
| VST | buckets/DCSHORTS/VST/VST.md | DCSHORTS |
| VVV | buckets/DRIVE/VVV/VVV.md | DRIVE |
| WAT | buckets/HCSUP/WAT/WAT.md | HCSUP |
| WIX | buckets/AGENTICS/WIX/WIX.md | AGENTICS |
| WK | buckets/AGENTICS/WK/WK.md | AGENTICS |
| WPP | buckets/AIOUT/WPP/WPP.md | AIOUT |
| WSO | buckets/BUILD/WSO/WSO.md | BUILD |
| WTKWY | buckets/DATASRVS/WTKWY/WTKWY.md | DATASRVS |
| WU | buckets/STABLECO/WU/WU.md | STABLECO |
| WULF | buckets/DCSHORTS/WULF/WULF.md | DCSHORTS |
| XHR | buckets/HOTEL/XHR/XHR.md | HOTEL |
| XPO | buckets/TRANSPOR/XPO/XPO.md | TRANSPOR |
| XYZ | buckets/STABLECO/XYZ/XYZ.md | STABLECO |
| YELP | buckets/MDAS/YELP/YELP.md | MDAS |
| Z | buckets/MTECH/Z/Z.md | MTECH |
| ZD | buckets/MDAS/ZD/ZD.md | MDAS |
| ZIP | buckets/AGENTICS/ZIP/ZIP.md | AGENTICS |
| ZTS | buckets/HCSUP/ZTS/ZTS.md | HCSUP |
<!-- END AUTO:GLOBAL_COMPANY_INDEX -->
## Manual Sections

Content inside the block below is user-owned and preserved on sync runs.

<!-- MOSAIC:BEGIN:MANUAL -->
_Add manual notes here. This block is preserved by sync._
<!-- MOSAIC:END:MANUAL -->
