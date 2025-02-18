def get_salary_in_line_series(df_data):
    mapping_salary_in_line = {
        "Yes": 1,
        "Mostly": 1,
        "Little payment": 2,
        "I believe that with my skills and educational background, I might be able to find a job with much higher salary than this, but the reason I applying here is to gain some experience first before I'm going to study abroad in the next 1-2 years.": 2,
        "No": 2,
        "The Salary quite under the market price": 2,
        "Work with family": 1,
        "Nope, pursued a different career. Had to start all over.": 2,
        "Not in line since MUIC students are all rounded, proficient in languages and can take on various roles efficiently.": 2,
        "Les than expected": 2,
        "the starting for a UX Designer is at least 30,000": 2,
        "Not really": 2,
        "Not sure": 2,
        "I think I can earn higher salaries compared with my friends": 2,
        "quite low even for fresh grad also not the job that i wanted to do": 2,
        "It is too little": 2,
        "Family business": 1,
        "Science students fresh grad usually earn 18000 for starter": 1,
        "I don't earn yet but when I do yes.": 1,
        "-": None,
        "Not make a sense": 2,
        "Too little": 2,
        "I think the start salary in Thailand is too low": 2,
        "If I work in the field I graduated the minimum income would be around 20,000 which would be more than what I earned now": 2,
        "the tuition fee was much higher than the salary": 2,
        "Salary in Thailand doesn’t align with the education cost": 2,
        "Below average due to contract role and not full time position": 2,
        "To low": 2,
        "I want to earn up to 26-27K": 2,
        "i think it should be around 25000": 2,
        "The position and experience in the field": 1,
        "Language and communication. Able to have business conversation with successful people and discuss business related.": 1,
        "Trying to make more": 2,
        "I get paid the same as other employees who don’t have English skill": 2,
        "No idea": 2,
        "Not enough for a our generation": 2,
        "It is a little low but thats okay because i still have support from my family and i get a lot of work benefits (healthcare, bonuses, etc)": 2,
        "I’m not sure": 2,
        "no, as I am project officer of multiple projects, research assistant for a research study, and assistant to principle course lecturer which provide me with heavy workload, technical support, and coordination beyond the salary rate that I currently received": 2,
        "It could be higher if I work with big corporates that match to the knowledge and skills I have learned from MUIC.": 2,
        "I prefer a salary more than 25K": 2,
        "I want 30,000": 2,
        "Because it's a family business, I don't expect income from this working position.": 1,
        "Regardless of my education certificate, I will get the position in my family business": 1,
        "Fixed salary as regulated by the government": 1,
        "I believe I can achieve higher salary however as working in a public sector, it is understandable": 2,
        "Approx should be 20-25k but if add on with the sv it should be acceptable": 1,
        "I think I should be able to earn more than this.": 2,
        "Large job scope + company’s budget": 1,
        "Want more": 2,
        "No because this is an inconsistent payment and It can not support even my basic needs.": 2,
        "Expected to receive a bit higher": 2,
        "Underpaid with our degree (Top 3 internation college  students in Thailand range should be 25k above)": 2,
        "No it is growth mindset 80%": 2,
        "I think since it's a international company, they can provide higher salary and it requires English skill, so 22,000 baht is quite low.": 2,
        "Undisclosed": None,
        "no, not with my quality": 2,
        "Could be better given the degree": 2,
        "Maybe": 2,
        "Work in different field": 2
    }
    
    return df_data['Is monthly salary in line with your qualification and education?'].map(mapping_salary_in_line)

def get_how_to_get_job_series(df_data):
    mapping_how_get_job = {
        "Family business": "0",
        "Agent contact me": "0",
        "ajarn.com": "0",
        "Career sites": "0",
        "CDP Group Chat": "0",
        "Company Facebook": "0",
        "Company website": "1",
        "Connection": "3",
        "Create by myself": "0",
        "Direct job offer from the team director.": "0",
        "Facebook": "0",
        "Facebook ads from the company to join paid internship (only for graduated student)": "0",
        "Facebook and websites": "0",
        "Family": "0",
        "Family": "0",
        "Family business": "0",
        "Family Business": "0",
        "family business": "0",
        "Family opportunity": "0",
        "family reccommendation": "0",
        "FB": "0",
        "Friend": "3",
        "Friend (MUIC)": "3",
        "From the MUIC Internship Program": "4",
        "Got offered": "0",
        "Got offered when being a trainee": "0",
        "HR contact after seeing my resume in Jobbkk": "0",
        "HR reached out through JobsDB": "0",
        "I interned there and got an offer": "0",
        "I was scouted": "0",
        "I’ve got an offer during my internship": "0",
        "Intern": "0",
        "Internship": "0",
        "internship": "0",
        "Internship ( 1st job)": "0",
        "Internship course": "0",
        "I've been an internship here before": "0",
        "Japan foreigners career support center": "0",
        "Job Board Website": "0",
        "Job hunting website": "0",
        "Job search app": "0",
        "job seeking website": "0",
        "Job website": "0",
        "JobDB": "0",
        "Jobs DB": "0",
        "Jobs seeking platform": "0",
        "JobsDB": "0",
        "Jobsdb": "0",
        "jobsdb website": "0",
        "Jobsdb.com": "0",
        "Linked In": "0",
        "LinkedIn": "0",
        "Linkedin": "0",
        "Linkedln": "0",
        "Linkin": "0",
        "linkedin": "0",
        "Muic alumni": "4",
        "MUIC Job Fair and Study Abroad Fair": "4",
        "MUIC Job Post on Alumni Career Line / Career Development Facebook": "4",
        "My own": "0",
        "Networking": "0",
        "Newspaper job post": "0",
        "Offer after Internship": "0",
        "Offer from internship": "0",
        "offer from internship": "0",
        "Own business": "0",
        "Private source": "3",
        "Reached from the company": "0",
        "Recommendations from friend": "3",
        "Recruitment Agency": "0",
        "Recruitment company": "0",
        "Refer": "3",
        "Referal from MU student": "3",
        "Referral": "3",
        "Referred by a mutual friend": "3",
        "Scholarship Commitment": "5",
        "Searching via JobsDB and contacted for interview then received job offer": "0",
        "Social media": "0",
        "Started my own social media page": "0",
        "Thai NGO website": "0",
        "third party website": "0",
        "UN jobs": "0",
        "Was an intern before being hired": "0",
        "Website": "1",
        "-": "0"
    }
    
    return df_data['How did you get your job?'].str.strip().map(mapping_how_get_job)


def get_how_to_get_job_text(df_data):
    # เรียกใช้ฟังก์ชัน get_how_to_get_job_series เพื่อรับ Series ของสถานะการทำงาน
    how_to_get_job_series = get_how_to_get_job_series(df_data)
    def map_data(row):
        value = str(how_to_get_job_series.loc[row.name])

        # ตรวจสอบเพิ่มเติมตามเงื่อนไขที่กำหนด
        if value == '0':
            # ถ้า how_to_get_job_series เท่ากับ '0' ตอบกลับเป็นค่า Do you have any problem in furthering your study?
            mapped_value = row['How did you get your job?'].strip()
        else:
            # ถ้า how_to_get_job_series เป็นค่าอื่นๆ ตอบกลับเป็นค่าว่าง
            mapped_value = ''

        return mapped_value
    
    return df_data.apply(map_data, axis=1)
    # return df_data.apply(lambda row: str(row['How did you get your job?']).strip() if str(how_to_get_job_series.loc[row.name]) == 0 else '', axis=1)


def get_alumni_commu_satisfy(df_data):
    mapping_alumni_commu_satisfy = {
        "Very satisfied": 1,       # พึงพอใจมาก
        "Satisfied": 2,            # พึงพอใจ
        "Unsure": 3,               # ไม่แน่ใจ
        "Dissatisfied": 4,         # ไม่พึงพอใจ
        "Very dissatisfied": 5     # ไม่พึงพอใจอย่างมาก
    }
    
    return df_data["How satisfied are you with Mahidol University's communication with alumni?"].map(mapping_alumni_commu_satisfy)

