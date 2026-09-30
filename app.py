"""
LOS CANTANTES DE MANILA
Tour Eligibility & Casting Priority Calculator
Organizational Decision-Support System | Version 1.0
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from io import BytesIO
import copy

st.set_page_config(
    page_title="LCDM Tour Eligibility & Casting Priority Calculator",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────
# CONSTANTS & DEFAULTS
# ─────────────────────────────────────────────────────────────

GATES = [
    "G1 Valid Membership",
    "G2 Active Membership",
    "G3 Tour Lock-In",
    "G4 Formal Commitment",
    "G5 Musical Readiness",
    "G6 Conduct/Good Standing",
    "G7 Availability",
    "G8 Financial Compliance (Bucket + Perf. Funds by Deadline)",
    "G9 Travel Documentation",
    "G10 Comp/Fest Requirements",
    "G11 Forms & Waivers",
    "G12 Admin Clearance",
]

RATING_CATS = {
    "A Musical (1-5)": {"weight": 30, "key": "musical"},
    "B Attendance (1-5)": {"weight": 20, "key": "attendance"},
    "C Conduct (1-5)": {"weight": 15, "key": "conduct"},
    "D Ensemble (1-5)": {"weight": 15, "key": "ensemble"},
    "E Sustained Part. (1-5)": {"weight": 10, "key": "sustained"},
    "F Tour Readiness (1-5)": {"weight": 10, "key": "tour_ready"},
}

PRIORITY_BANDS = [
    (90, "PRIORITY A — HIGHLY READY"),
    (80, "PRIORITY B — STRONGLY READY"),
    (70, "PRIORITY C — READY"),
    (60, "PRIORITY D — CONDITIONAL"),
    (0, "BELOW PRIORITY THRESHOLD"),
]

DEFAULT_MEMBERS = [
    {"Member ID": "LCDM-001", "Full Name": "Adarlo, Christine Dayrest Fiñones", "Voice Part": "Soprano 1", "Secondary Voice Part": "Soprano 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "adarloday@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-002", "Full Name": "Agapay, Anthea Rose Argañosa", "Voice Part": "Soprano 2", "Secondary Voice Part": "Soprano 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "Anthearose23@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-003", "Full Name": "Alcera, Jasmine Marie Perfas", "Voice Part": "Soprano 2", "Secondary Voice Part": "Soprano 2", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "jmariejazz23@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-004", "Full Name": "Aure, Jaedzhel Chyle Maverick Dayrit", "Voice Part": "Bass 1", "Secondary Voice Part": "Bass 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "jaedaure@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-005", "Full Name": "Baes, Meridith Mygiel Santiago", "Voice Part": "Soprano 1", "Secondary Voice Part": "Soprano 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "mrdthmygl@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-006", "Full Name": "Bendal, Diomelyn Desumala", "Voice Part": "Alto 2", "Secondary Voice Part": "Alto 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "diomelyn.bendal@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": "Passport renewal in progress"},
    {"Member ID": "LCDM-007", "Full Name": "Bulauitan, Jazmine Kim Tan Terles", "Voice Part": "Soprano 2", "Secondary Voice Part": "Soprano 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "kim.bulauitan@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-008", "Full Name": "Cameña, Alexis Janelle Cada", "Voice Part": "Alto 2", "Secondary Voice Part": "Alto 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "alexis.camena03@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": "Recently joined"},
    {"Member ID": "LCDM-009", "Full Name": "Cameña, Alyanna Joice Cada", "Voice Part": "Soprano 1", "Secondary Voice Part": "Soprano 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "alyannajoice24@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-010", "Full Name": "Cailles, Jubilee Ballesteros", "Voice Part": "Soprano 2", "Secondary Voice Part": "Soprano 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "bilyballesteros@yahoo.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": "Returning for this tour"},
    {"Member ID": "LCDM-011", "Full Name": "Cailles, Emmanuel Marie Locsin", "Voice Part": "Tenor 1", "Secondary Voice Part": "Tenor 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "maricailles@yahoo.com.ph", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-012", "Full Name": "Caluza, Booz Waief Gayatin", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 2", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "caluza12@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-013", "Full Name": "Clemente, Danielle Margaret Gozano", "Voice Part": "Alto 1", "Secondary Voice Part": "Alto 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "margarettclemente20@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-014", "Full Name": "Concepcion, Kent Nathaniel", "Voice Part": "Tenor 1", "Secondary Voice Part": "Tenor 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "concepcionkentnathaniel@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-015", "Full Name": "Datiles, Laurence Dela Cruz", "Voice Part": "Bass 1", "Secondary Voice Part": "Alto 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "laurencedatiles14@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-016", "Full Name": "De Leon, Angel Nichole Feliciano", "Voice Part": "Soprano 2", "Secondary Voice Part": "Bass 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "anicholedeleon@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-017", "Full Name": "Del Mundo, Ralph Yuan Aquino", "Voice Part": "Bass 2", "Secondary Voice Part": "Bass 2", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "yuandelmundo4@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-018", "Full Name": "Doroteo, Jaily Anzon Lavariño", "Voice Part": "Soprano 1", "Secondary Voice Part": "Soprano 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "ajdoroteo22@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-019", "Full Name": "Duron, Jamaica Costob", "Voice Part": "Alto 2", "Secondary Voice Part": "Alto 2", "Membership Status": "Member on Leave", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "On Leave", "Section": "Alto", "Contact Email": "jamaicaduron03@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-020", "Full Name": "Escober, Camille Francisco", "Voice Part": "Alto 1", "Secondary Voice Part": "Alto 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "escobercamille08@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-021", "Full Name": "Facto, Carl Elmore Santiago", "Voice Part": "Bass 2", "Secondary Voice Part": "Bass 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "dokcarl@yahoo.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-022", "Full Name": "Galvan, Bernadette Dela Cruz", "Voice Part": "Soprano 2", "Secondary Voice Part": "Soprano 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Soprano", "Contact Email": "bernagalvan15@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-023", "Full Name": "Garcia, Crizthyne Kyle Maynete", "Voice Part": "Alto 2", "Secondary Voice Part": "Alto 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "crzthyn23@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-024", "Full Name": "Geronimo, Cherie Love Joy Vila", "Voice Part": "Alto 1", "Secondary Voice Part": "Alto 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "cherieljscarlet@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-025", "Full Name": "Lopez, Paul Andrew David", "Voice Part": "Bass 1", "Secondary Voice Part": "Bass 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "paulandrewlopez204@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-026", "Full Name": "Morales, Laurence John Rapadas", "Voice Part": "Bass 2", "Secondary Voice Part": "Bass 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "psychonyxdorotheos@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-027", "Full Name": "Muit, Jack Jerson Jr. Achivar", "Voice Part": "Tenor 1", "Secondary Voice Part": "Tenor 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "jackjersonm@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-028", "Full Name": "Nakpil, Kieth Kyno Marqueda", "Voice Part": "Bass 1", "Secondary Voice Part": "Bass 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "nakpilkyno@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-029", "Full Name": "Ormita, Lance Martin Regala", "Voice Part": "Bass 1", "Secondary Voice Part": "Bass 1", "Membership Status": "Regular Trainee", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "lanceormita@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-030", "Full Name": "Pador, John Leif Terence Fernandez", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "jltpador@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-031", "Full Name": "Realengo, Paulo Lim", "Voice Part": "Bass 2", "Secondary Voice Part": "Bass 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "plrealengo42@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-032", "Full Name": "Riego, Stephen Aiken", "Voice Part": "Bass 2", "Secondary Voice Part": "Bass 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Bass", "Contact Email": "iamstephenken@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-033", "Full Name": "Rodriguez, Prince Brendan", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "princebrendanb@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-034", "Full Name": "Romero, Edgar II Gañas", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "ragde2oremor99@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-035", "Full Name": "Sigua, Sushmita Piraman", "Voice Part": "Alto 1", "Secondary Voice Part": "Alto 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Alto", "Contact Email": "sushmitasigua23@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-036", "Full Name": "Silvestre, John Eric Nagal", "Voice Part": "Tenor 1", "Secondary Voice Part": "Tenor 1", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "je.silvestre23@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-037", "Full Name": "Tirona, Daniel Kevin", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "kevz_morgley@yahoo.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-038", "Full Name": "Vasquez, Mark Ulysses Albestor", "Voice Part": "Tenor 2", "Secondary Voice Part": "Tenor 2", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Tenor", "Contact Email": "markulyssesvasquez@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
    {"Member ID": "LCDM-039", "Full Name": "Vargas, Darwin Bajar", "Voice Part": "Conductor", "Secondary Voice Part": "Conductor", "Membership Status": "Full Member", "Date Joined LCDM": "2020-06-04", "Active Since": "2020-06-04", "Current Status": "Active", "Section": "Conductor", "Contact Email": "loscantantesdemanila@gmail.com", "Passport Status": "Valid", "Visa Status": "Pending", "Notes": ""},
]

# Sample assessment data matching the source file (for demo)
SAMPLE_ASSESSMENTS = {
    "LCDM-001": {"gates": ["YES"]*12, "ratings": [5,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-002": {"gates": ["YES"]*12, "ratings": [4,5,4,4,4,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-003": {"gates": ["YES","YES","YES","YES","YES","YES","YES","NO","YES","YES","YES","YES"], "ratings": [5,5,5,5,5,5], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-004": {"gates": ["YES"]*12, "ratings": [4,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-005": {"gates": ["YES"]*12, "ratings": [4,4,3,4,3,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-006": {"gates": ["YES"]*12, "ratings": [4,4,4,4,3,3], "selection": "RESERVE", "bucket": "YES", "funds": "YES"},
    "LCDM-007": {"gates": ["YES"]*12, "ratings": [5,4,5,4,5,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-008": {"gates": ["YES"]*12, "ratings": [4,3,4,3,1,3], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-009": {"gates": ["YES"]*12, "ratings": [4,5,4,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-010": {"gates": ["YES"]*12, "ratings": [4,3,3,3,2,3], "selection": "RESERVE", "bucket": "YES", "funds": "YES"},
    "LCDM-011": {"gates": ["YES"]*12, "ratings": [5,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-012": {"gates": ["YES"]*12, "ratings": [3,5,4,4,4,4], "selection": "RESERVE", "bucket": "YES", "funds": "YES"},
    "LCDM-013": {"gates": ["YES","YES","YES","YES","YES","YES","YES","YES","NO","YES","YES","YES"], "ratings": [5,5,5,5,5,5], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-014": {"gates": ["YES"]*12, "ratings": [5,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-015": {"gates": ["YES"]*12, "ratings": [5,4,3,4,3,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-016": {"gates": ["YES"]*12, "ratings": [4,4,4,4,3,3], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-017": {"gates": ["YES"]*12, "ratings": [4,4,5,4,5,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-018": {"gates": ["YES"]*12, "ratings": [3,3,4,3,1,3], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-019": {"gates": ["YES","NO","NO","YES","YES","YES","YES","YES","YES","YES","YES","YES"], "ratings": [5,2,4,5,4,5], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-020": {"gates": ["YES"]*12, "ratings": [5,2,3,3,2,3], "selection": "RESERVE", "bucket": "YES", "funds": "YES"},
    "LCDM-021": {"gates": ["YES"]*12, "ratings": [5,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-022": {"gates": ["YES"]*12, "ratings": [4,5,4,4,4,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-023": {"gates": ["YES"]*12, "ratings": [5,5,5,5,5,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-024": {"gates": ["YES"]*12, "ratings": [3,5,5,5,4,5], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-025": {"gates": ["YES"]*12, "ratings": [4,4,3,4,3,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-026": {"gates": ["YES"]*12, "ratings": [4,4,4,4,3,3], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-027": {"gates": ["YES"]*12, "ratings": [5,4,5,4,5,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-028": {"gates": ["YES"]*12, "ratings": [4,3,4,3,1,3], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-029": {"gates": ["YES"]*12, "ratings": [4,5,4,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-030": {"gates": ["YES"]*12, "ratings": [3,3,3,3,2,3], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-031": {"gates": ["YES"]*12, "ratings": [5,5,5,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-032": {"gates": ["YES"]*12, "ratings": [4,5,4,4,4,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-033": {"gates": ["YES"]*12, "ratings": [5,5,5,5,5,5], "selection": "", "bucket": "YES", "funds": "YES"},
    "LCDM-034": {"gates": ["YES"]*12, "ratings": [3,5,5,5,4,5], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-035": {"gates": ["YES"]*12, "ratings": [4,4,3,4,3,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-036": {"gates": ["YES"]*12, "ratings": [4,4,4,4,3,3], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-037": {"gates": ["YES"]*12, "ratings": [5,4,5,4,5,4], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-038": {"gates": ["YES"]*12, "ratings": [4,3,4,3,1,3], "selection": "NOT SELECTED", "bucket": "YES", "funds": "YES"},
    "LCDM-039": {"gates": ["YES"]*12, "ratings": [4,5,4,5,4,5], "selection": "SELECTED", "bucket": "YES", "funds": "YES"},
}

# ─────────────────────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────────────────────

def init_state():
    if "tour" not in st.session_state:
        st.session_state.tour = {
            "name": "European Competition Tour 2027",
            "destination": "Bulgaria/Latvia/Germany",
            "type": "Competition",
            "departure": date(2027, 10, 7),
            "return": date(2027, 11, 7),
            "lock_in_months": 6,
            "early_commit_months": 8,
            "min_musical": 19,
            "min_overall": 70,
            "max_roster": 33,
            "male_min": 16,
            "female_min": 16,
            "sop_min": 8,
            "alto_min": 8,
            "tenor_min": 8,
            "bass_min": 8,
            "other_reqs": "Must meet host competition age/registration rules; SATB balance preferred",
            "fin_deadline": date(2027, 8, 7),
            "bucket_amount": 25000,
            "perf_funds_policy": "Funds acquired from LCDM performances/concerts credited to the member's tour account must be fully applied or reconciled by the Financial Compliance Deadline.",
        }
    if "members" not in st.session_state:
        st.session_state.members = pd.DataFrame(DEFAULT_MEMBERS)
    if "assessments" not in st.session_state:
        # Build full assessment records
        assessments = {}
        for mid, data in SAMPLE_ASSESSMENTS.items():
            assessments[mid] = {
                "gates": data["gates"],
                "ratings": data["ratings"],
                "selection": data.get("selection", ""),
                "bucket": data.get("bucket", "NO"),
                "funds": data.get("funds", "NO"),
                "notes": "",
                "assessor": "Carl Facto",
            }
        st.session_state.assessments = assessments
    if "exceptions" not in st.session_state:
        st.session_state.exceptions = []
    if "history" not in st.session_state:
        st.session_state.history = []

init_state()

# ─────────────────────────────────────────────────────────────
# CORE CALCULATION ENGINE
# ─────────────────────────────────────────────────────────────

def calc_lock_in_date(departure, months):
    # Approximate month subtraction
    year = departure.year
    month = departure.month - months
    while month <= 0:
        month += 12
        year -= 1
    day = min(departure.day, 28)  # safe day
    return date(year, month, day)

def months_between(start, end):
    return (end.year - start.year) * 12 + (end.month - start.month)

def compute_member(member_row, assessment, tour):
    mid = member_row["Member ID"]
    gates = assessment.get("gates", ["NO"] * 12)
    ratings = assessment.get("ratings", [0] * 6)
    selection = assessment.get("selection", "")
    bucket = assessment.get("bucket", "NO")
    funds = assessment.get("funds", "NO")

    # Eligibility
    any_no = any(g == "NO" for g in gates)
    any_blank = any(g not in ("YES", "NO") for g in gates)
    if any_no:
        eligibility = "INELIGIBLE"
    elif any_blank:
        eligibility = "PENDING"
    else:
        eligibility = "ELIGIBLE FOR CASTING PRIORITY"

    # Weighted scores
    musical = (ratings[0] / 5 * 30) if ratings[0] else 0
    attendance = (ratings[1] / 5 * 20) if ratings[1] else 0
    conduct = (ratings[2] / 5 * 15) if ratings[2] else 0
    ensemble = (ratings[3] / 5 * 15) if ratings[3] else 0
    sustained = (ratings[4] / 5 * 10) if ratings[4] else 0
    tour_ready = (ratings[5] / 5 * 10) if ratings[5] else 0
    total = musical + attendance + conduct + ensemble + sustained + tour_ready

    # Priority class
    if eligibility == "INELIGIBLE":
        priority = "INELIGIBLE"
    elif eligibility == "PENDING":
        priority = "PENDING"
    else:
        priority = "BELOW PRIORITY THRESHOLD"
        for thresh, label in PRIORITY_BANDS:
            if total >= thresh:
                priority = label
                break

    # Musical min
    musical_min_met = "YES" if musical >= tour["min_musical"] else "NO — BELOW MUSICAL MINIMUM"

    # Auto status
    if eligibility == "INELIGIBLE":
        auto_status = "INELIGIBLE"
    elif eligibility == "PENDING":
        auto_status = "PENDING"
    elif musical < tour["min_musical"]:
        auto_status = "NOT RECOMMENDED (MUSICAL MIN)"
    elif total < tour["min_overall"]:
        auto_status = "BELOW OVERALL THRESHOLD"
    else:
        auto_status = f"ELIGIBLE — {priority.split(' — ')[0]}"

    # Lock-in
    try:
        active_since = pd.to_datetime(member_row["Active Since"]).date()
    except Exception:
        active_since = tour["departure"]
    lock_in_date = calc_lock_in_date(tour["departure"], tour["lock_in_months"])
    months_active = months_between(active_since, date.today())
    lock_in_ok = "YES" if months_active >= tour["lock_in_months"] else "NO"

    # Financial status
    if bucket == "YES" and funds == "YES":
        fin_status = "COMPLETE BY DEADLINE"
    else:
        fin_status = "INCOMPLETE"

    # Tour-only risk (simple heuristic)
    tour_only = "LOW"
    if ratings[4] <= 2:
        tour_only = "MODERATE"
    if ratings[4] <= 1:
        tour_only = "HIGH"

    return {
        "Member ID": mid,
        "Full Name": member_row["Full Name"],
        "Voice Part": member_row["Voice Part"],
        "Membership Status": member_row["Membership Status"],
        "Section": member_row.get("Section", ""),
        "Eligibility": eligibility,
        "Musical /30": round(musical, 1),
        "Attendance /20": round(attendance, 1),
        "Conduct /15": round(conduct, 1),
        "Ensemble /15": round(ensemble, 1),
        "Sustained /10": round(sustained, 1),
        "Tour Ready /10": round(tour_ready, 1),
        "TOTAL /100": round(total, 1),
        "Priority Class": priority,
        "Musical Min Met?": musical_min_met,
        "Auto Status": auto_status,
        "Selection": selection,
        "Tour-Only Risk": tour_only,
        "Lock-In Status": lock_in_ok,
        "Months Active": months_active,
        "Bucket Complete": bucket,
        "Funds Reconciled": funds,
        "Financial Status": fin_status,
        "gates": gates,
        "ratings": ratings,
    }

def get_all_computed():
    tour = st.session_state.tour
    members = st.session_state.members
    assessments = st.session_state.assessments
    results = []
    for _, row in members.iterrows():
        mid = row["Member ID"]
        a = assessments.get(mid, {"gates": ["NO"]*12, "ratings": [0]*6, "selection": "", "bucket": "NO", "funds": "NO"})
        results.append(compute_member(row, a, tour))
    return pd.DataFrame(results)

def section_from_voice(vp):
    vp = str(vp).lower()
    if "soprano" in vp:
        return "Soprano"
    if "alto" in vp:
        return "Alto"
    if "tenor" in vp:
        return "Tenor"
    if "bass" in vp:
        return "Bass"
    if "conductor" in vp:
        return "Conductor"
    return "Other"

# ─────────────────────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────────────────────

st.sidebar.title("🎵 LCDM Tour Calculator")
st.sidebar.caption("Decision-Support System v1.0")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    [
        "README / Governance",
        "1. Tour Setup",
        "2. Member Database",
        "3. Tour Assessment",
        "4. Casting Roster",
        "5. Voice Balance",
        "6. Dashboard",
        "7. Rubric (Reference)",
        "8. Exception Log",
        "9. Casting Report",
    ],
    index=0,
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**Core Principle**\n\n"
    "ELIGIBILITY = Can this member be considered? (Pass/Fail gates)\n\n"
    "CASTING PRIORITY = Among eligible members, how strong is priority? (100-pt score)"
)

# ─────────────────────────────────────────────────────────────
# PAGE: README
# ─────────────────────────────────────────────────────────────

if page == "README / Governance":
    st.title("LOS CANTANTES DE MANILA")
    st.subheader("Tour Eligibility & Casting Priority Calculator")
    st.caption("Organizational Decision-Support System  |  Version 1.0  |  For Artistic Director, Artistic Team & Tour Management")

    st.markdown("---")
    st.markdown("### PURPOSE & GOVERNANCE PRINCIPLE")
    st.info(
        "This application is a **DECISION-SUPPORT TOOL**, not an autonomous artistic decision-maker. "
        "It produces objective eligibility determination and measurable casting priority scores. "
        "Final casting decisions remain with the authorized Artistic/Management body and may depend on "
        "repertoire, voice-part balance, competition regulations, ensemble sound, staging, and operational constraints."
    )

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**ELIGIBILITY**")
        st.write('"Can this member be considered?" — Pass/Fail mandatory gates')
    with col2:
        st.markdown("**CASTING PRIORITY**")
        st.write('"Among eligible members, how strong is this member\'s priority for this tour roster?" — 100-point weighted score')

    st.markdown("### DECISION HIERARCHY (STRICT ORDER)")
    st.markdown("""
1. **MANDATORY ELIGIBILITY GATES** (Pass/Fail) — If ANY gate = NO → INELIGIBLE (score cannot override)  
2. If all gates = YES → Proceed to weighted 100-point Casting Priority Assessment  
3. Musical & Technical minimum (19/30) must be met for final casting consideration  
4. Overall Priority Score → Priority Band (A/B/C/Conditional/Below Threshold)  
5. Artistic / Roster Need (voice balance, repertoire, ensemble) → Final Casting Decision  
6. Authorized users may mark SELECTED / RESERVE / NOT SELECTED / WITHDRAWN
""")

    st.markdown("### SCORING ARCHITECTURE (100 POINTS)")
    score_df = pd.DataFrame([
        {"Category": "A. Musical & Technical Readiness", "Weight": "30 pts", "Measures": "Pitch, rhythm, technique, diction, repertoire mastery, response to conductor"},
        {"Category": "B. Attendance & Commitment", "Weight": "20 pts", "Measures": "Rehearsal attendance, punctuality, preparation, reliability"},
        {"Category": "C. Conduct, Attitude & Professionalism", "Weight": "15 pts", "Measures": "Respect, accountability, receptiveness to feedback, policy compliance"},
        {"Category": "D. Ensemble Suitability & Artistic Contribution", "Weight": "15 pts", "Measures": "Blend, balance, sectional contribution, ensemble awareness (tour-specific)"},
        {"Category": "E. Sustained LCDM Participation", "Weight": "10 pts", "Measures": "Ongoing contribution beyond tour preparation (discourages tour-only membership)"},
        {"Category": "F. Tour Readiness & Administrative Reliability", "Weight": "10 pts", "Measures": "Documents, briefings, deadlines, travel preparedness"},
    ])
    st.dataframe(score_df, use_container_width=True, hide_index=True)

    st.markdown("### IMPORTANT SAFEGUARDS")
    st.warning("""
- Financial capacity / additional contributions do **NOT** generate casting priority points (compliance gate only).  
- Seniority alone, personal relationships, popularity, or social status do **NOT** increase priority.  
- Tenure may be used only as a contextual tie-breaker when scores and artistic suitability are substantially similar.  
- Any override of a mandatory eligibility gate requires documented reason + authorized approval in the Exception Log.  
- **Gate 8 (Financial Compliance)** is NON-NEGOTIABLE: Personal Tour Bucket + performance-acquired funds must be completed by the deadline.
""")

    st.markdown("### QUICK START")
    st.markdown("""
1. Go to **Tour Setup** → Enter tour name, destination, dates, minimum scores, roster size, and voice requirements.  
2. Go to **Member Database** → Ensure all potential tour members are listed with correct voice parts and status.  
3. Go to **Tour Assessment** → For each member, complete all YES/NO mandatory gates and 1–5 ratings. Eligibility and scores calculate automatically.  
4. Review **Casting Roster** (sorted by priority) and **Voice Balance**. Mark SELECTED / RESERVE as appropriate.  
5. Use **Dashboard** for management overview and **Casting Report** for formal documentation.
""")

    st.caption("© Los Cantantes de Manila / The Manila Choral Collective  |  Internal Use Only")

# ─────────────────────────────────────────────────────────────
# PAGE: TOUR SETUP
# ─────────────────────────────────────────────────────────────

elif page == "1. Tour Setup":
    st.title("TOUR SETUP / CONTROL PANEL")
    st.caption("Authorized users may modify parameters below. All other pages reference these values.")

    tour = st.session_state.tour

    st.markdown("### TOUR IDENTITY")
    c1, c2 = st.columns(2)
    with c1:
        tour["name"] = st.text_input("Tour Name", tour["name"])
        tour["destination"] = st.text_input("Destination / Country", tour["destination"])
        tour["type"] = st.selectbox("Tour Type", ["Competition", "Concert Tour", "Festival", "Exchange", "Other"], index=0)
    with c2:
        tour["departure"] = st.date_input("Departure Date", tour["departure"])
        tour["return"] = st.date_input("Return Date", tour["return"])

    st.markdown("### LOCK-IN & THRESHOLDS")
    c1, c2, c3 = st.columns(3)
    with c1:
        tour["lock_in_months"] = st.number_input("Required Lock-In Period (months)", 1, 24, tour["lock_in_months"])
        tour["early_commit_months"] = st.number_input("Preferred Early Commitment (months)", 1, 24, tour["early_commit_months"])
    with c2:
        tour["min_musical"] = st.number_input("Minimum Musical Score (/30)", 0, 30, tour["min_musical"])
        tour["min_overall"] = st.number_input("Minimum Overall Priority Score (/100)", 0, 100, tour["min_overall"])
    with c3:
        tour["max_roster"] = st.number_input("Maximum Roster Size", 1, 100, tour["max_roster"])
        lock_date = calc_lock_in_date(tour["departure"], tour["lock_in_months"])
        early_date = calc_lock_in_date(tour["departure"], tour["early_commit_months"])
        st.metric("Required Lock-In Date (auto)", str(lock_date))
        st.metric("Early Commitment Date (auto)", str(early_date))

    st.markdown("### VOICE / SECTION REQUIREMENTS")
    c1, c2, c3 = st.columns(3)
    with c1:
        tour["male_min"] = st.number_input("Male Voice Requirement (min)", 0, 50, tour["male_min"])
        tour["female_min"] = st.number_input("Female Voice Requirement (min)", 0, 50, tour["female_min"])
    with c2:
        tour["sop_min"] = st.number_input("Soprano Requirement (min)", 0, 30, tour["sop_min"])
        tour["alto_min"] = st.number_input("Alto Requirement (min)", 0, 30, tour["alto_min"])
    with c3:
        tour["tenor_min"] = st.number_input("Tenor Requirement (min)", 0, 30, tour["tenor_min"])
        tour["bass_min"] = st.number_input("Bass Requirement (min)", 0, 30, tour["bass_min"])
    tour["other_reqs"] = st.text_area("Other Artistic / Competition Requirements", tour["other_reqs"])

    st.markdown("### FINANCIAL COMPLIANCE (NON-NEGOTIABLE GATE)")
    c1, c2 = st.columns(2)
    with c1:
        tour["fin_deadline"] = st.date_input("Financial Compliance Deadline", tour["fin_deadline"])
        tour["bucket_amount"] = st.number_input("Personal Tour Bucket Required Amount", 0, 1_000_000, tour["bucket_amount"], step=1000)
    with c2:
        st.info(
            "**NON-NEGOTIABLE:** Member must complete (1) Personal Tour Bucket AND (2) reconciliation of acquired performance funds "
            "by the scheduled Financial Compliance Deadline. If either is incomplete at deadline → Gate 8 = NO → INELIGIBLE. "
            "Additional voluntary contributions beyond the required bucket do NOT increase casting priority points."
        )
    tour["perf_funds_policy"] = st.text_area("Performance Funds Policy", tour["perf_funds_policy"])

    st.session_state.tour = tour
    st.success("Tour parameters saved to session. All calculations now use these values.")

# ─────────────────────────────────────────────────────────────
# PAGE: MEMBER DATABASE
# ─────────────────────────────────────────────────────────────

elif page == "2. Member Database":
    st.title("MEMBER MASTER DATABASE")
    st.caption("Maintain accurate member records. Voice Part and Membership Status use dropdowns.")

    df = st.session_state.members.copy()

    # Editable data editor
    edited = st.data_editor(
        df,
        use_container_width=True,
        num_rows="dynamic",
        column_config={
            "Member ID": st.column_config.TextColumn("Member ID", width="small"),
            "Full Name": st.column_config.TextColumn("Full Name", width="medium"),
            "Voice Part": st.column_config.SelectboxColumn(
                "Voice Part",
                options=["Soprano 1", "Soprano 2", "Alto 1", "Alto 2", "Tenor 1", "Tenor 2", "Bass 1", "Bass 2", "Conductor"],
            ),
            "Secondary Voice Part": st.column_config.SelectboxColumn(
                "Secondary Voice Part",
                options=["Soprano 1", "Soprano 2", "Alto 1", "Alto 2", "Tenor 1", "Tenor 2", "Bass 1", "Bass 2", "Conductor", ""],
            ),
            "Membership Status": st.column_config.SelectboxColumn(
                "Membership Status",
                options=["Full Member", "Regular Trainee", "Member on Leave", "Inactive", "Alumni"],
            ),
            "Current Status": st.column_config.SelectboxColumn(
                "Current Status",
                options=["Active", "On Leave", "Inactive"],
            ),
            "Section": st.column_config.SelectboxColumn(
                "Section",
                options=["Soprano", "Alto", "Tenor", "Bass", "Conductor"],
            ),
            "Passport Status": st.column_config.SelectboxColumn(
                "Passport Status",
                options=["Valid", "Expired", "Pending Renewal", "None"],
            ),
            "Visa Status": st.column_config.SelectboxColumn(
                "Visa Status",
                options=["Valid", "Pending", "Not Required", "Denied"],
            ),
        },
        hide_index=True,
        key="member_editor",
    )
    if st.button("💾 Save Member Database"):
        st.session_state.members = edited
        st.success(f"Saved {len(edited)} members.")

    st.markdown(f"**Total members:** {len(st.session_state.members)}")

# ─────────────────────────────────────────────────────────────
# PAGE: TOUR ASSESSMENT
# ─────────────────────────────────────────────────────────────

elif page == "3. Tour Assessment":
    st.title("TOUR ASSESSMENT — ELIGIBILITY GATES + CASTING PRIORITY SCORE")
    st.caption("Complete YES/NO gates and 1–5 ratings. Scores calculate automatically. If ANY mandatory gate = NO → INELIGIBLE.")

    members = st.session_state.members
    mid_list = members["Member ID"].tolist()
    selected_mid = st.selectbox("Select Member to Assess", mid_list, format_func=lambda x: f"{x} — {members.loc[members['Member ID']==x, 'Full Name'].values[0]}")

    mrow = members[members["Member ID"] == selected_mid].iloc[0]
    a = st.session_state.assessments.get(selected_mid, {
        "gates": ["YES"] * 12,
        "ratings": [3] * 6,
        "selection": "",
        "bucket": "NO",
        "funds": "NO",
        "notes": "",
        "assessor": "",
    })

    st.markdown(f"### {mrow['Full Name']}  ({mrow['Voice Part']})  —  {mrow['Membership Status']}")

    # Gates
    st.markdown("#### MANDATORY ELIGIBILITY GATES (YES / NO)")
    gate_cols = st.columns(4)
    new_gates = []
    for i, gname in enumerate(GATES):
        with gate_cols[i % 4]:
            val = a["gates"][i] if i < len(a["gates"]) else "YES"
            new_val = st.selectbox(gname, ["YES", "NO"], index=0 if val == "YES" else 1, key=f"gate_{selected_mid}_{i}")
            new_gates.append(new_val)

    # Ratings
    st.markdown("#### CASTING PRIORITY RATINGS (1–5)")
    rating_cols = st.columns(6)
    new_ratings = []
    for i, (cat, meta) in enumerate(RATING_CATS.items()):
        with rating_cols[i]:
            val = a["ratings"][i] if i < len(a["ratings"]) else 3
            new_val = st.slider(cat, 1, 5, int(val), key=f"rate_{selected_mid}_{i}")
            new_ratings.append(new_val)

    # Financial tracking
    st.markdown("#### FINANCIAL TRACKING (supports Gate 8)")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        bucket = st.selectbox("Personal Tour Bucket Complete?", ["YES", "NO"], index=0 if a.get("bucket") == "YES" else 1, key=f"bucket_{selected_mid}")
    with fc2:
        funds = st.selectbox("Perf. Funds Reconciled?", ["YES", "NO"], index=0 if a.get("funds") == "YES" else 1, key=f"funds_{selected_mid}")
    with fc3:
        selection = st.selectbox("Selection Decision", ["", "SELECTED", "RESERVE", "NOT SELECTED", "WITHDRAWN"],
                                 index=["", "SELECTED", "RESERVE", "NOT SELECTED", "WITHDRAWN"].index(a.get("selection", "")),
                                 key=f"sel_{selected_mid}")

    notes = st.text_area("Selection / Assessor Notes", a.get("notes", ""), key=f"notes_{selected_mid}")
    assessor = st.text_input("Assessor", a.get("assessor", ""), key=f"assessor_{selected_mid}")

    if st.button("💾 Save Assessment for this Member", type="primary"):
        st.session_state.assessments[selected_mid] = {
            "gates": new_gates,
            "ratings": new_ratings,
            "selection": selection,
            "bucket": bucket,
            "funds": funds,
            "notes": notes,
            "assessor": assessor,
        }
        st.success(f"Assessment saved for {selected_mid}")

    # Live computed view
    st.markdown("---")
    st.markdown("#### LIVE COMPUTED RESULT")
    computed = compute_member(mrow, {
        "gates": new_gates,
        "ratings": new_ratings,
        "selection": selection,
        "bucket": bucket,
        "funds": funds,
    }, st.session_state.tour)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Eligibility", computed["Eligibility"])
    m2.metric("TOTAL /100", computed["TOTAL /100"])
    m3.metric("Priority Class", computed["Priority Class"].split(" — ")[0] if " — " in computed["Priority Class"] else computed["Priority Class"])
    m4.metric("Musical Min Met?", computed["Musical Min Met?"])

    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    sc1.metric("Musical /30", computed["Musical /30"])
    sc2.metric("Attendance /20", computed["Attendance /20"])
    sc3.metric("Conduct /15", computed["Conduct /15"])
    sc4.metric("Ensemble /15", computed["Ensemble /15"])
    sc5.metric("Sustained /10", computed["Sustained /10"])
    sc6.metric("Tour Ready /10", computed["Tour Ready /10"])

    st.write(f"**Auto Status:** {computed['Auto Status']}  |  **Tour-Only Risk:** {computed['Tour-Only Risk']}  |  **Lock-In:** {computed['Lock-In Status']} ({computed['Months Active']} months active)")

# ─────────────────────────────────────────────────────────────
# PAGE: CASTING ROSTER
# ─────────────────────────────────────────────────────────────

elif page == "4. Casting Roster":
    st.title("TOUR CASTING & ROSTER BUILDER — RANKED ELIGIBLE MEMBERS")
    st.caption("Members ranked by calculated priority. Final artistic decisions remain with the Artistic Director.")

    df = get_all_computed()
    df_eligible = df[df["Eligibility"] == "ELIGIBLE FOR CASTING PRIORITY"].copy()
    df_eligible = df_eligible.sort_values("TOTAL /100", ascending=False).reset_index(drop=True)
    df_eligible.insert(0, "Rank", range(1, len(df_eligible) + 1))

    show_all = st.checkbox("Show all members (including ineligible)", value=False)
    display_df = df.sort_values("TOTAL /100", ascending=False) if show_all else df_eligible

    st.dataframe(
        display_df[["Rank", "Member ID", "Full Name", "Voice Part", "Eligibility", "TOTAL /100", "Priority Class",
                    "Musical /30", "Attendance /20", "Ensemble /15", "Auto Status", "Selection"]].rename(columns={"TOTAL /100": "Total Score"})
        if "Rank" in display_df.columns else
        display_df[["Member ID", "Full Name", "Voice Part", "Eligibility", "TOTAL /100", "Priority Class",
                    "Musical /30", "Attendance /20", "Ensemble /15", "Auto Status", "Selection"]].rename(columns={"TOTAL /100": "Total Score"}),
        use_container_width=True,
        hide_index=True,
        height=600,
    )

    st.markdown(f"**Eligible pool:** {len(df_eligible)}  |  **Selected:** {(df['Selection']=='SELECTED').sum()}  |  **Reserve:** {(df['Selection']=='RESERVE').sum()}")

# ─────────────────────────────────────────────────────────────
# PAGE: VOICE BALANCE
# ─────────────────────────────────────────────────────────────

elif page == "5. Voice Balance":
    st.title("VOICE-PART / ROSTER BALANCE PLANNER")
    st.caption("Required numbers come from Tour Setup. Eligible and Selected counts are calculated from assessments.")

    tour = st.session_state.tour
    df = get_all_computed()

    # Map to broad sections
    def broad_section(vp):
        vp = str(vp).lower()
        if "soprano" in vp: return "Soprano"
        if "alto" in vp: return "Alto"
        if "tenor" in vp: return "Tenor"
        if "bass" in vp: return "Bass"
        return "Other"

    df["Broad"] = df["Voice Part"].apply(broad_section)

    eligible = df[df["Eligibility"] == "ELIGIBLE FOR CASTING PRIORITY"]
    selected = df[df["Selection"] == "SELECTED"]

    sections = ["Soprano", "Alto", "Tenor", "Bass"]
    reqs = [tour["sop_min"], tour["alto_min"], tour["tenor_min"], tour["bass_min"]]

    rows = []
    for sec, req in zip(sections, reqs):
        elig = len(eligible[eligible["Broad"] == sec])
        sel = len(selected[selected["Broad"] == sec])
        gap = sel - req
        status = "SUFFICIENT" if gap >= 0 else ("SELECT FROM ELIGIBLE" if elig >= req else "SHORTAGE")
        rows.append({"VOICE SECTION": sec, "Required (min)": req, "Eligible": elig, "Selected": sel, "Gap (Selected − Required)": gap, "Status": status})

    bal_df = pd.DataFrame(rows)
    st.dataframe(bal_df, use_container_width=True, hide_index=True)

    # Male / Female
    st.markdown("### MALE / FEMALE SUMMARY")
    fem_elig = len(eligible[eligible["Broad"].isin(["Soprano", "Alto"])])
    mal_elig = len(eligible[eligible["Broad"].isin(["Tenor", "Bass"])])
    fem_sel = len(selected[selected["Broad"].isin(["Soprano", "Alto"])])
    mal_sel = len(selected[selected["Broad"].isin(["Tenor", "Bass"])])

    mf = pd.DataFrame([
        {"Category": "Female (Sop+Alto)", "Required": tour["female_min"], "Eligible": fem_elig, "Selected": fem_sel},
        {"Category": "Male (Ten+Bass)", "Required": tour["male_min"], "Eligible": mal_elig, "Selected": mal_sel},
    ])
    st.dataframe(mf, use_container_width=True, hide_index=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Maximum Roster Size", tour["max_roster"])
    c2.metric("Currently Selected", len(selected))
    c3.metric("Remaining Slots", tour["max_roster"] - len(selected))

# ─────────────────────────────────────────────────────────────
# PAGE: DASHBOARD
# ─────────────────────────────────────────────────────────────

elif page == "6. Dashboard":
    tour = st.session_state.tour
    st.title("EXECUTIVE KPI DASHBOARD — TOUR ELIGIBILITY & CASTING")
    st.caption(f"{tour['name']}  |  {tour['departure']} to {tour['return']}  |  {tour['destination']}")

    df = get_all_computed()
    eligible = df[df["Eligibility"] == "ELIGIBLE FOR CASTING PRIORITY"]
    ineligible = df[df["Eligibility"] == "INELIGIBLE"]
    selected = df[df["Selection"] == "SELECTED"]
    reserve = df[df["Selection"] == "RESERVE"]

    st.markdown("### ELIGIBILITY KPIs")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Assessed", len(df))
    c2.metric("Eligible", len(eligible))
    c3.metric("Ineligible", len(ineligible))
    c4.metric("Pending", len(df[df["Eligibility"] == "PENDING"]))
    rate = len(eligible) / len(df) if len(df) else 0
    c5.metric("Eligibility Rate", f"{rate:.0%}")

    st.markdown("### PRIORITY KPIs (Eligible Only)")
    pri_a = len(eligible[eligible["Priority Class"].str.contains("PRIORITY A", na=False)])
    pri_b = len(eligible[eligible["Priority Class"].str.contains("PRIORITY B", na=False)])
    pri_c = len(eligible[eligible["Priority Class"].str.contains("PRIORITY C", na=False)])
    pri_d = len(eligible[eligible["Priority Class"].str.contains("PRIORITY D", na=False)])
    below = len(eligible[eligible["Priority Class"].str.contains("BELOW", na=False)])
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Priority A", pri_a)
    c2.metric("Priority B", pri_b)
    c3.metric("Priority C", pri_c)
    c4.metric("Conditional (D)", pri_d)
    c5.metric("Below Threshold", below)

    st.markdown("### ARTISTIC KPIs (Averages among Eligible)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg Musical /30", f"{eligible['Musical /30'].mean():.1f}" if len(eligible) else "—")
    c2.metric("Avg Overall /100", f"{eligible['TOTAL /100'].mean():.1f}" if len(eligible) else "—")
    c3.metric("Avg Attendance /20", f"{eligible['Attendance /20'].mean():.1f}" if len(eligible) else "—")
    c4.metric("Avg Ensemble /15", f"{eligible['Ensemble /15'].mean():.1f}" if len(eligible) else "—")

    st.markdown("### ROSTER KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Target Roster Size", tour["max_roster"])
    c2.metric("Eligible Pool", len(eligible))
    c3.metric("Selected", len(selected))
    c4.metric("Reserve", len(reserve))

    st.markdown("### COMPLIANCE KPIs (Gate Pass Rates among all assessed)")
    # Approximate from stored assessments
    g8_yes = sum(1 for a in st.session_state.assessments.values() if a.get("gates", ["NO"]*12)[7] == "YES")
    g9_yes = sum(1 for a in st.session_state.assessments.values() if a.get("gates", ["NO"]*12)[8] == "YES")
    total_a = len(st.session_state.assessments) or 1
    c1, c2, c3 = st.columns(3)
    c1.metric("Financially Cleared (G8)", f"{g8_yes} ({g8_yes/total_a:.0%})")
    c2.metric("Travel Docs Complete (G9)", f"{g9_yes} ({g9_yes/total_a:.0%})")
    c3.metric("Selected vs Target", f"{len(selected)} / {tour['max_roster']}")

    st.markdown("### TRAFFIC-LIGHT SUMMARY")
    health = "GREEN — Strong pool" if rate >= 0.8 else ("YELLOW — Moderate" if rate >= 0.5 else "RED — Weak pool")
    musical_ok = "GREEN — Most meet musical min" if (eligible["Musical Min Met?"] == "YES").mean() > 0.8 else "YELLOW — Some musical gaps"
    roster_fill = "GREEN — Near capacity" if len(selected) >= tour["max_roster"] * 0.9 else ("YELLOW — Slots remaining" if len(selected) >= tour["max_roster"] * 0.5 else "RED — Significant slots remaining")
    st.write(f"**Overall Eligibility Health:** {health}")
    st.write(f"**Musical Standard:** {musical_ok}")
    st.write(f"**Roster Fill Status:** {roster_fill}")

# ─────────────────────────────────────────────────────────────
# PAGE: RUBRIC
# ─────────────────────────────────────────────────────────────

elif page == "7. Rubric (Reference)":
    st.title("OBJECTIVE SCORING RUBRIC — 1 TO 5 DESCRIPTORS")
    st.caption("Assessors must use these descriptors. Scores are objective anchors, not relative popularity rankings.")

    with st.expander("CATEGORY A — MUSICAL & TECHNICAL READINESS (Weight: 30 points)  |  Minimum required: 19/30", expanded=True):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Below Required Standard | Significant pitch/rhythm issues; technique insufficient for tour repertoire; limited response to conductor; cannot maintain standard under pressure. |
| 2 | Developing | Inconsistent intonation or rhythm; technique still developing; partial repertoire mastery; needs substantial coaching to reach tour standard. |
| 3 | Competent | Meets basic technical standard; generally accurate pitch and rhythm; adequate diction and breath support; can perform repertoire with preparation. |
| 4 | Strong | Reliable intonation and rhythm; solid technique and diction; good dynamic control and interpretation; responsive to conductor; performs consistently under pressure. |
| 5 | Exceptional | Excellent pitch, rhythm, technique, and interpretation; exemplary diction and breath control; highly responsive; elevates ensemble standard; fully tour-ready. |
""")

    with st.expander("CATEGORY B — ATTENDANCE & COMMITMENT (Weight: 20 points)"):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Unsatisfactory | Frequent unexplained absences; often late; unprepared; poor communication about conflicts. |
| 2 | Developing | Irregular attendance; occasional lateness; incomplete preparation; inconsistent communication. |
| 3 | Satisfactory | Acceptable attendance; generally punctual; adequately prepared; communicates absences in advance. |
| 4 | Strong | High attendance; punctual; well-prepared; reliable; proactive communication. |
| 5 | Exceptional | Near-perfect attendance and punctuality; thoroughly prepared; highly reliable; supports sectional readiness. |
""")

    with st.expander("CATEGORY C — CONDUCT, ATTITUDE & PROFESSIONALISM (Weight: 15 points)"):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Unsatisfactory | Disrespectful behavior; resists feedback; creates conflict; does not represent LCDM positively. |
| 2 | Developing | Inconsistent professionalism; occasional resistance to direction; needs guidance on conduct. |
| 3 | Satisfactory | Respectful; accepts feedback; follows policies; appropriate communication. |
| 4 | Strong | Consistently professional; receptive to feedback; accountable; positive influence on peers. |
| 5 | Exemplary | Models respect and maturity; highly receptive; resolves issues constructively; strong ambassador for LCDM. |
""")

    with st.expander("CATEGORY D — ENSEMBLE SUITABILITY & ARTISTIC CONTRIBUTION (Weight: 15 points)  |  TOUR-SPECIFIC"):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Poor Fit | Does not blend; balance issues; limited ensemble awareness; weak sectional contribution for this repertoire. |
| 2 | Developing | Inconsistent blend/balance; developing listening skills; limited adaptability to formation/repertoire needs. |
| 3 | Suitable | Adequate blend and balance; listens; contributes to section; acceptable for tour ensemble. |
| 4 | Strong Contribution | Strong blend and balance; excellent listening; supports section; adaptable; enhances ensemble sound. |
| 5 | Exceptional Contribution | Exemplary blend, balance, and awareness; elevates section and ensemble; highly versatile for repertoire and staging. |
""")

    with st.expander("CATEGORY E — SUSTAINED LCDM PARTICIPATION & ORGANIZATIONAL COMMITMENT (Weight: 10 points)"):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Minimal | Little participation outside tour prep; appears primarily for international engagement. |
| 2 | Limited | Sporadic non-tour involvement; limited contribution to ordinary activities. |
| 3 | Satisfactory | Regular participation in rehearsals/concerts; some involvement beyond tour. |
| 4 | Strong | Consistent contribution to concerts, workshops, projects; reliable organizational presence. |
| 5 | Sustained / Exceptional | Long-term, multi-faceted contribution; section/committee leadership; models sustained membership. |
""")

    with st.expander("CATEGORY F — TOUR READINESS & ADMINISTRATIVE RELIABILITY (Weight: 10 points)"):
        st.markdown("""
| Rating | Label | Descriptors |
|--------|-------|-------------|
| 1 | Poor | Misses deadlines; incomplete documents; unreliable communication; unprepared for travel protocols. |
| 2 | Developing | Often late with requirements; needs repeated reminders; incomplete understanding of protocols. |
| 3 | Satisfactory | Meets most deadlines; documents generally complete; adequate communication and preparedness. |
| 4 | Strong | Timely submission; complete documents; responsive; understands and follows tour protocols. |
| 5 | Fully Ready | Proactive and complete; excellent communication; fully prepared; supports others with process. |
""")

    st.warning("NOTE: Financial capacity, additional voluntary contributions, seniority alone, personal relationships, popularity, and social status must NOT be used to increase any of the above ratings.")

# ─────────────────────────────────────────────────────────────
# PAGE: EXCEPTION LOG
# ─────────────────────────────────────────────────────────────

elif page == "8. Exception Log":
    st.title("EXCEPTION / OVERRIDE LOG")
    st.caption("Any override of a mandatory eligibility gate requires documented reason, policy basis, and authorized approval.")

    with st.form("exception_form"):
        st.markdown("#### Record New Exception")
        c1, c2 = st.columns(2)
        with c1:
            mid = st.selectbox("Member ID", st.session_state.members["Member ID"].tolist())
            original = st.text_input("Original Result (e.g. INELIGIBLE)")
            override = st.text_input("Override Requested")
        with c2:
            reason = st.text_area("Reason")
            policy = st.text_input("Policy Basis")
            requested_by = st.text_input("Requested By")
            approved_by = st.text_input("Approved By")
        final_dec = st.selectbox("Final Decision", ["EXCEPTION GRANTED — ELIGIBLE", "EXCEPTION DENIED", "PENDING REVIEW"])
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Add Exception Log Entry")
        if submitted:
            entry = {
                "Log ID": f"EXC-{len(st.session_state.exceptions)+1:03d}",
                "Member ID": mid,
                "Member Name": st.session_state.members.loc[st.session_state.members["Member ID"]==mid, "Full Name"].values[0],
                "Original Result": original,
                "Override Requested": override,
                "Reason": reason,
                "Policy Basis": policy,
                "Requested By": requested_by,
                "Approved By": approved_by,
                "Date": str(date.today()),
                "Final Decision": final_dec,
                "Notes": notes,
            }
            st.session_state.exceptions.append(entry)
            st.success("Exception logged.")

    if st.session_state.exceptions:
        st.dataframe(pd.DataFrame(st.session_state.exceptions), use_container_width=True, hide_index=True)
    else:
        st.info("No exceptions recorded yet.")

    st.markdown("""
**INSTRUCTIONS**  
1. Do not override a mandatory gate without completing this log.  
2. Original Result = the automatic eligibility outcome before override.  
3. Final Decision must be recorded.  
4. Approval must come from an authorized officer (Artistic Director / designated Tour Officer).  
5. Keep supporting documentation with organizational records.
""")

# ─────────────────────────────────────────────────────────────
# PAGE: CASTING REPORT
# ─────────────────────────────────────────────────────────────

elif page == "9. Casting Report":
    tour = st.session_state.tour
    st.title("TOUR CASTING DECISION REPORT")
    st.caption("Print-ready formal report for management approval.")

    df = get_all_computed()
    selected = df[df["Selection"] == "SELECTED"].sort_values("TOTAL /100", ascending=False)
    reserve = df[df["Selection"] == "RESERVE"].sort_values("TOTAL /100", ascending=False)
    eligible = df[df["Eligibility"] == "ELIGIBLE FOR CASTING PRIORITY"]

    st.markdown("### TOUR INFORMATION")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.write(f"**Tour Name:** {tour['name']}")
        st.write(f"**Destination:** {tour['destination']}")
        st.write(f"**Tour Type:** {tour['type']}")
    with c2:
        st.write(f"**Departure:** {tour['departure']}")
        st.write(f"**Return:** {tour['return']}")
        st.write(f"**Roster Capacity:** {tour['max_roster']}")
    with c3:
        st.write(f"**Total Assessed:** {len(df)}")
        st.write(f"**Eligible:** {len(eligible)}")
        st.write(f"**Ineligible:** {len(df[df['Eligibility']=='INELIGIBLE'])}")
        st.write(f"**Eligibility Rate:** {len(eligible)/len(df):.0%}" if len(df) else "—")

    st.markdown("### FINAL CAST (SELECTED)")
    if len(selected):
        st.dataframe(
            selected[["Member ID", "Full Name", "Voice Part", "TOTAL /100", "Priority Class", "Musical /30", "Selection"]].rename(columns={"TOTAL /100": "Total Score"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.warning("No members marked SELECTED yet.")

    st.markdown("### RESERVE CAST")
    if len(reserve):
        st.dataframe(
            reserve[["Member ID", "Full Name", "Voice Part", "TOTAL /100", "Priority Class", "Musical /30", "Selection"]].rename(columns={"TOTAL /100": "Total Score"}),
            use_container_width=True, hide_index=True
        )
    else:
        st.info("No reserve members.")

    st.markdown("### VOICE-PART DISTRIBUTION (SELECTED)")
    def broad(vp):
        vp = str(vp).lower()
        if "soprano" in vp: return "Soprano"
        if "alto" in vp: return "Alto"
        if "tenor" in vp: return "Tenor"
        if "bass" in vp: return "Bass"
        return "Other"
    if len(selected):
        dist = selected["Voice Part"].apply(broad).value_counts().reindex(["Soprano", "Alto", "Tenor", "Bass"], fill_value=0)
        dist_df = pd.DataFrame({"Section": dist.index, "Count": dist.values})
        st.dataframe(dist_df, use_container_width=True, hide_index=True)
        st.write(f"**Total Selected:** {len(selected)}")

    st.markdown("### INELIGIBLE / OUTSTANDING REQUIREMENTS")
    st.write(
        "Review Tour Assessment for members marked INELIGIBLE or PENDING. Common outstanding items: "
        "failed lock-in, incomplete Personal Tour Bucket or unreconciled performance funds (Gate 8), "
        "missing documentation, musical minimum not met, or incomplete gates. "
        "Financial compliance is non-negotiable. Use Exception Log for any authorized overrides."
    )

    st.markdown("---")
    st.markdown("### APPROVAL & AUTHORIZATION")
    st.markdown("""
| Role | Name | Signature | Date |
|------|------|-----------|------|
| Artistic Director | _________________________ | _________________________ | __________ |
| Tour / Project Manager | _________________________ | _________________________ | __________ |
| Authorized Officer | _________________________ | _________________________ | __________ |
""")
    st.caption("This report is a decision-support document. Final artistic and operational responsibility remains with the authorized Artistic and Management body of Los Cantantes de Manila.")

    # Export button
    if st.button("📥 Download Full Computed Roster (CSV)"):
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "lcdm_casting_roster.csv", "text/csv")
