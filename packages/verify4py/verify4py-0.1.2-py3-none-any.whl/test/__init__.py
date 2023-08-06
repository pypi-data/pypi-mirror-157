from verify4py.UniversityDiplomaIssuer import UniversityDiplomaIssuer

if __name__ == "__main__":
    issuer = UniversityDiplomaIssuer('0x6754f91fE274378B5Bb08E131Eb14A417F161CC8', 'https://node-testnet.corexchain.io',
                                     '0x259164d9D26a1bcC8aE3B721aC23F0e2A5563D07', 'test12', 3305)
    meta_data = {
        "DEGREE_NUMBER": "D202201954",
        "PRIMARY_IDENTIFIER_NUMBER": "ук92040781",
        "INSTITUTION_ID": 35580,
        "INSTITUTION_NAME": "МУБИС /Монгол улсын боловсролын их сургууль/",
        "EDUCATION_LEVEL_NAME": "Бакалаврын боловсрол",
        "EDUCATION_FIELD_CODE": "011402",
        "EDUCATION_FIELD_NAME": "Багш, байгалийн ухааны боловсрол",
        "TOTAL_GPA": 3.4,
        "LAST_NAME": "Батсуурь",
        "FIRST_NAME": "Отгонтуяа",
        "CONFER_YEAR_NAME": "2021-2022 хичээлийн жил"
    }
    issuer.issue_pdf('D202201954', '/home/surenbayar/test.pdf', '/home/surenbayar/test_verified.pdf',
                     meta_data, 0, '', '', '65245c75a01178dae360ba4e1df32f8a0058cf92ba8b325c3ce0be4eb340c945')
