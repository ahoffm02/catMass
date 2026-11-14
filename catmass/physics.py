"""catMass physics core: every number v3 reports, with no GUI imports.

Ported from `legacy/catMass_2023v3_singlefile_EXE-REFERENCE.py` (parity-rebuild Stage 4).
This is a structure-only port. Formulas, constants, units, defaults, string formats and error
messages are unchanged, including the known v3 defects (vault plan, "Findings from golden
generation"), except for the approved changes listed in tests/approved_changes.py. Each change
is its own commit, marked "Change F<n>" where it acts.

Layout:
1. Custom materials v3 registers with xraydb at launch.
2. v3's module-level physics functions, copied verbatim (tests/test_parity_v3.py checks every
   character against the reference).
3. Physics that lived inside v3's GUI methods, lifted into plain functions. Expressions are
   copied unchanged; inputs that v3 read from text boxes arrive as the same strings.
4. Input validation (change F7): bad input returns an 'ERROR - ...' message instead of raising.
   The UI calls calculate_result, dilute_sample, build_metal_sample, build_complex_sample,
   plot_data, transmission_panel and ion_chamber_absorbed, which all validate first.

Inputs keep v3's conventions: energies in eV unless noted, areas in cm^2, masses returned in mg,
thicknesses in the v3 unit-combo index convention (see `unitconvert`).

Not here (UI behavior, checked end to end at Stage 5): which box a value is read from, stale
displays after toggling angle mode, silent fallbacks to a previous value, plot styling.
"""
import math
import os

import numpy as np
import xraydb
import xraylib
from xraydb import materials as _xraydb_materials


# =============================================================================================
# 1. Custom materials (reference lines 49-62)
# =============================================================================================
def add_material_in_memory(name, formula, density, categories=None):
    """Add a material to xraydb's table for this session only.

    Change F11 (finding 11, approved by the researcher 2026-11-08): v3 used xraydb.add_material,
    which also rewrites the user's materials file (xraydb/materials.dat in the user config
    folder) on every call, so each launch appended duplicate lines. This does the same in-memory
    steps as xraydb 4.5.4's add_material and skips the file write. Every material, value and
    list order is unchanged (tests/test_approved_changes.py).
    Assumption (HC16): relies on xraydb's internal table (materials._materials,
    _read_materials_db, Material), which is fixed by the pinned xraydb version.
    """
    if _xraydb_materials._materials is None:
        _xraydb_materials._materials = _xraydb_materials._read_materials_db()
    formula = formula.replace(' ', '')
    if categories is None:
        categories = []
    _xraydb_materials._materials[name.lower()] = _xraydb_materials.Material(
        formula, float(density), name, categories)


def register_custom_materials():
    """Register v3's five extra materials with xraydb, with v3's names and values.

    v3 called xraydb.add_material; this uses add_material_in_memory (change F11).
    """
    ## PEEK material added to database gm/cm^3
    add_material_in_memory('PEEK', 'C19H14O3', 1.32, categories=['polymer'])
    ## glassy carbon material added to database
    add_material_in_memory('Glossy Carbon', 'C', 1.5, categories=['polymer'])

    ## Kanthal A-1 Wire material added to database
    #https://www.kanthal.com/en/products/material-datasheets/strip/kanthal-a-1/#:~:text=Kanthal%C2%AE%20A%2D1%20is,and%20very%20good%20oxidation%20resistance.
    add_material_in_memory('Kanthal A-1', 'Cr1.83AlFe6.139', 7.1, categories=['polymer'])

    ## NiCr Wire material added to database
    add_material_in_memory('Nichrome', 'CrNi3.544', 8.4, categories=['polymer'])

    ## NiCr Wire material added to database
    add_material_in_memory('Carbon Fiber', 'C3HN', 1.184, categories=['polymer'])


register_custom_materials()


# =============================================================================================
# 2. v3 module-level physics functions (reference lines 3529-4214), verbatim
# =============================================================================================
# --- XASMassCalc: reference lines 3529-3729, verbatim ---
def XASMassCalc(Sample, Element, Edge, Area, AL, gamma = 50 ,delta = 50):
    '''
    

    Parameters
    ----------
    Sample : TYPE
        DESCRIPTION.
    Element : TYPE
        DESCRIPTION.
    Edge : TYPE
        DESCRIPTION.
    Area : TYPE
        DESCRIPTION.
    AL : TYPE, optional
        DESCRIPTION. The default is 2.6.
    delta : TYPE, optional
        DESCRIPTION. The default is 50.

    Returns
    -------
    Error_Statement : TYPE
        DESCRIPTION.
    E0 : TYPE
        DESCRIPTION.
    mass : TYPE
        DESCRIPTION.
    step : TYPE
        DESCRIPTION.

    '''
    
    '''
    Calculates the Edge energy [eV], sample mass [mg] and transmission edge step
    based upon a stoichiometric sample composition, the element and corresponding
    edge to be probed, the perpendicular cross-sectional area of the sample to
    the beam, desired total absorption lenght "delta" eV above the edge.
    
    delta is used to calcualte the absorption coefficient at E0+/-delta to determine
    the edge step

    Parameters
    ----------
    Sample : STR
        Chemcial formula of the sample. parentheses can be used. Numbers of 
        atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Element : STR
        Element in the sample at whihc to caluclate the absorption properties around.
    Edge : STR
        ['K', 'L1', 'L2', 'L3'] used to determine the edge energy of Element.
    Area : FLOAT
        [units = cm^2] cross-sectional area of sample in the X-ray beam. When
        determining sample mass, assume cross-sectional area of entire sample
        area in sample holder is being illuminated.
    AL : FLOAT, optional
        Desired total absorption cross-section of the sample at delta eV above
        the edge. Tthe default is 2.6.
    delta : FLOAT, optional
        Energy [eV] aove the edge energy to calcualte the sampel mass at and energy
        around the edge energy [E0+/- delta] to calcualte the tranmission edge
        step. The default is 50.

    Returns
    -------
    Error_Statement : STR
        Error message to diagnose input failures.
    E0 : FLOAT
        Energy [eV] of the absopriton edge of the Element
    mass : FLOAT
        Mass [mg] calcuated based upon sample composition, energy, area, and total absorption
    step : FLOAT
        Estimated edge step of the element assuming transmission geometry

    '''
    
    ERROR1 = 'ERROR - Sample not Defined'
    ERROR2 = 'ERROR - Element to be Scanned not Defined'
    ERROR3 = 'ERROR - Absorption Length not Defined'
    ERROR4 = 'ERROR - Sample Area not Defined'
    ERROR5 = 'ERROR - Absorption Length not Defined'
    #delta = 50 #eV
    
    delta = delta/1000  #converted to keV forxraylib
    gamma = gamma/1000
    
    Error_Statement = 'None'
    E0 = 0
    mass = 0
    step = 0
    #AL = 0
       

    if Sample == '':
        Error_Statement = ERROR1
        return Error_Statement, E0, mass, step, AL
    
    elif Element == '':
        Error_Statement = ERROR2
        return Error_Statement, E0, mass, step, AL
    
    elif AL == '':
        Error_Statement = ERROR3
        return Error_Statement, E0, mass, step, AL
    
    elif Area == '':
        Error_Statement = ERROR4
        return Error_Statement, E0, mass, step, AL
    elif AL == '':
        Error_Statement = ERROR5
        return Error_Statement, E0, mass, step, AL
    
    else:
    
        #Convert Strings to Floats
        
        
        Al = float(AL)
        
        
        
        
        
        #if Area == '3 mm Capillary':
            #Area = '0.3'
        #elif Area == '1 mm Capillary':
            #Area = '0.1'
        #elif Area == 'Pellet':
            #Area = '0.38'       
        #elif Area == 'Other':
           # Area = Area  
        
        area = float(Area)
        
        #Extract Chemcial Information from Sample
        Elements = xraylib.CompoundParser(Sample)

        #Identify Edge Energy
        if Edge == 'K':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),0)
        elif Edge == 'L1':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),1)
        elif Edge == 'L2':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),2)        
        elif Edge == 'L3':
            E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element),3)  
        else:
            E0 = float(Edge)/1000




        if Elements['nElements']>1:
            # Determine Photabsorption Cross Sections for each element at E0 +/- 50 eV
            Photo_XS = []
            for x in range(0,Elements['nElements']):
                if x == 0:
                    Photo_XS = [xraylib.CS_Photo(Elements['Elements'][x], E0-delta), xraylib.CS_Photo(Elements['Elements'][x], E0+gamma)]
                else:
                    newPXS = [xraylib.CS_Photo(Elements['Elements'][x], E0-delta),xraylib.CS_Photo(Elements['Elements'][x], E0+gamma)]
                    Photo_XS = np.vstack((Photo_XS,newPXS)) 

            # Calcualte Mass Weighted Photo Absorption Cross Section:
            mu_tot = []
            for x in range(0,Elements['nElements']):
                if x ==0:
                    mu_tot = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
                else:
                    new_mu = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
                    mu_tot = np.vstack((mu_tot, new_mu))
                    
            mu_ave = np.sum(mu_tot, axis = 0)

            # Calculate Sample mass @ E0 + 50 eV and edge step

            mass = Al*area/mu_ave[1]
            E0 = E0*1000

            #step = np.multiply(np.divide(np.multiply(Elements['massFractions'], mass), area), np.subtract(Photo_XS[:,1], Photo_XS[:,0]))
            #step = np.max(step)
            step = np.multiply(np.divide(np.multiply(1, mass), area), np.subtract(mu_ave[1], mu_ave[0]))
            #step2 = mass/area*(mu_ave[1] - mu_ave[0])
            #print(step2)
            #step = np.max(step)
            mass = mass*1000
    
            return Error_Statement, E0, mass, step, mu_ave[1]
    
        else:
            # Determine Photabsorption Cross Sections for element at E0 +/- 50 eV
            Photo_XS = [xraylib.CS_Photo(Elements['Elements'][0], E0-delta), xraylib.CS_Photo(Elements['Elements'][0], E0+gamma)]
        
            # Calculate Sample mass @ E0 + 50 eV and edge step

            mass = Al*area/Photo_XS[1]
            step = (mass/area)*(Photo_XS[1]-Photo_XS[0])
            E0 = E0*1000
            mass = mass*1000
            mu_ave = Photo_XS[1]
            #mu ave should not be vector should be caluculated for single element option...
            return Error_Statement, E0, mass, step, mu_ave


# --- XASPLOTTER: reference lines 3731-3736, verbatim ---
def XASPLOTTER(Sample, Element, Edge, Area, AL, gamma ,gamma2,delta = 50):
    #from src import functions as fct
    
    Result2, Enot2, ms2, stp3 ,muave = XASMassCalc(Sample, Element, Edge, Area, AL, gamma, delta = 50)
    
    return muave


# --- XASStoichCalc: reference lines 3741-3857, verbatim ---
def XASStoichCalc(Sample1, Sample2, Sample1_DR, Sample2_DR):
    '''
    Calculates the combined chemical formula for a sample and a diluement given
    a ratio of mass components.

    Parameters
    ----------
    Sample1 : STR
        Chemcial formula of the sample. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Sample2 : STR
        Chemcial formula of the diluent. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Sample1_DR : INT or FLOAT
        Mass of the first sample wiht respect to the second. E.g. if the ratio was
        Sample1:Sample2 = 1:5, Sample1_DR = 1.
    Sample2_DR : INT or FLOAT
        Mass of the second sample wiht respect to the first. E.g. if the ratio was
        Sample1:Sample2 = 1:5, Sample2_DR = 5.


    Returns
    -------
    Error_message : STR
        Error message used to identify problems in the funciton inputs.
    Diluted_Sample_Formula : STR
        Chemical formula of the mixing of two samples givne theri mass dilution ratios
    '''
    ERROR1 = 'ERROR - Sample Not Defined'
    ERROR2 = 'ERROR - Dilution Ratio Not Defined'
    
    Error_message = 'None'
    Diluted_Sample_Formula = ''
    
    if Sample1 == '':
        Error_message = ERROR1
        return Error_message, Diluted_Sample_Formula
    
    elif Sample2 != '' and Sample2_DR == '':
        Error_message = ERROR2
        return Error_message, Diluted_Sample_Formula
    
    elif Sample1 != '' and Sample2 != '' and Sample2_DR != '' and Sample1_DR == '':
        Error_message = ERROR2
        return Error_message, Diluted_Sample_Formula
    
    else:
        
        if Sample2 == '':
            Diluted_Sample_Formula = Sample1
            return Error_message, Diluted_Sample_Formula
            
        else:
            
            if Sample1_DR == '':
                Sample1_dR = 1
            else:
                Sample1_dR = float(Sample1_DR)
            
            Sample2_dR = float(Sample2_DR)
            
            # Parse the compounds
            Sample_Elements = xraylib.CompoundParser(Sample1)

            Diluent_Elements = xraylib.CompoundParser(Sample2)
        
        
            #Calculate New Nass Fractions
            Updated_MF = []
    
            for x in range(0,Sample_Elements['nElements']):
                if x == 0:
                    Updated_MF = [Sample_Elements['Elements'][x], Sample_Elements['massFractions'][x]*Sample1_dR/(Sample1_dR + Sample2_dR)]
                else:
                    new_line = [Sample_Elements['Elements'][x], Sample_Elements['massFractions'][x]*Sample1_dR/(Sample1_dR + Sample2_dR)]    
                    Updated_MF = np.vstack((Updated_MF,new_line))

            if Sample2_dR > 0:
                for x in range(0,Diluent_Elements['nElements']):
                    new_line = [Diluent_Elements['Elements'][x], Diluent_Elements['massFractions'][x]*Sample2_dR/(Sample1_dR + Sample2_dR)]   
                    Updated_MF = np.vstack((Updated_MF,new_line)) 

            #Calcualte Moles of each component
            mol = []
            for x in range(0,np.shape(Updated_MF)[0]):
                if x == 0:
                    mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                else:
                    new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                    mol = np.vstack((mol,new_mol))
        
            mol = mol/min(mol)

            #Build New String
            for x in range(0,np.shape(Updated_MF)[0]):
                if x == 0:
                    Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
                else:
                    new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                    Sample_String = Sample_String+new_String



            Diluted_Sample = xraylib.CompoundParser(Sample_String)

            #Build Condensed String

            for x in range(0,Diluted_Sample['nElements']):
                if x == 0:
                    Diluted_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Diluted_Sample['Elements'][x])), float(Diluted_Sample['nAtoms'][x])) 
                else:
                    new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Diluted_Sample['Elements'][x])), float(Diluted_Sample['nAtoms'][x]))
                    Diluted_String = Diluted_String+new_String
        
            return Error_message, Diluted_String


# --- metalCalculateSample: reference lines 3861-3988, verbatim ---
def metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support):
    '''
    Calculates the chemical formula of a material consiting of two metal site compositsions,
    weight loadings, and a support.

    Parameters
    ----------
    Metal_Site1 : STR
        Chemcial formula of the metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal1_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Metal_Site2 : STR
        Chemcial formula of a second metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal2_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Support : STR
        Chemcial formula of the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.

    Returns
    -------
    Sample_String : STR
        Chemical ormula of sample defined by support, metal site(s) and loadings.

    '''
    
    ERROR1 = 'ERROR - Metal Site 1 Not Defined'
    ERROR2 = 'ERROR - Metal Site 1 Loading Not Defined'
    ERROR3 = 'ERROR - Metal Loading (Site 2) Not Defined'
    ERROR4 = 'ERROR - Support Not Defined'
    
    if Support == '':
        return ERROR4

    elif Metal_Site1 == '':
        return ERROR1
    
    elif Metal1_Loading == '':
        return ERROR2   
    
    elif Metal_Site2 != '' and Metal2_Loading == '':
            return ERROR3
    
    else:        
        Metal_Loading1 = float(Metal1_Loading)
               
        # Parse metal Site 1 and Support 
        MetalSite1_Elements = xraylib.CompoundParser(Metal_Site1)
        
        Support_Elements = xraylib.CompoundParser(Support)
    
   
        #Calculate New Nass Fractions
        Updated_MF = []
    
        if Metal_Site2 == '':
            #Weight metal site 1 fractions and store them + atomic number
            for x in range(0,MetalSite1_Elements['nElements']):
                if x == 0:
                    Updated_MF = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]
                else:
                    new_line = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]   
                    Updated_MF = np.vstack((Updated_MF,new_line))
                    
            #Add Support Mass Fractions
            for x in range(0,Support_Elements['nElements']):
                new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-(Metal_Loading1)/100)]   
                Updated_MF = np.vstack((Updated_MF,new_line))
        
        else:
            #Weight metal site 1 fractions and store them + atomic number      
            for x in range(0,MetalSite1_Elements['nElements']):
                if x == 0:
                    Updated_MF = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]
                else:
                    new_line = [MetalSite1_Elements['Elements'][x], MetalSite1_Elements['massFractions'][x]*Metal_Loading1/100]   
                    Updated_MF = np.vstack((Updated_MF,new_line))
        
            #Weight metal site 2 fractions and store them + atomic number      
            MetalSite2_Elements = xraylib.CompoundParser(Metal_Site2)
            Metal_Loading2 = float(Metal2_Loading)
            for x in range(0,MetalSite2_Elements['nElements']):
                new_line = [MetalSite2_Elements['Elements'][x], MetalSite2_Elements['massFractions'][x]*Metal_Loading2/100]   
                Updated_MF = np.vstack((Updated_MF,new_line))
                
            #Add Support Mass Fractions
            for x in range(0,Support_Elements['nElements']):
                new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-(Metal_Loading1+Metal_Loading2)/100)]   
                Updated_MF = np.vstack((Updated_MF,new_line))
    
        
        #Calcualte Moles of each component
        mol = []
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
            else:
                new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                mol = np.vstack((mol,new_mol))
        
        mol = mol/min(mol)

       
        #Build New String
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                Sample_String = Sample_String+new_String

        Constructed_Sample = xraylib.CompoundParser(Sample_String)

        
        #Build Condensed String
        for x in range(0,Constructed_Sample['nElements']):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x]))
                Sample_String = Sample_String+new_String
        
        return Sample_String


# --- ComplexCalculateSample: reference lines 3991-4098, verbatim ---
def ComplexCalculateSample(Complex, Metal_Loading, Metal_Site, Support):
    '''
    Calculate the stoichiometry of a supported complex catalyst based upon the complex,
    its loading, or the metal center and its loading, and the support

    Parameters
    ----------
    Complex : STR
        Chemcial formula of the metal site on the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.
    Metal_Loading : INT or FLOAT
        [%] Weight % loading of first metal site.
    Metal_Site : STR
        Element in the complex
    Support : STR
        Chemcial formula of the support. parentheses, even nested, can be used. 
        Numbers of atoms are placed to the left of the atomic symbol (case sensitive)
        with no special characters. E.g. 'H2' or H2O, Na2SO4, or Pt0.5MgO.

    Returns
    -------
    Sample_String : STR
        Chemical ormula of sample defined by support, metal site(s) and loadings.

    '''
               
    ERROR1 = 'ERROR - Metal Complex Not Defined'
    ERROR2 = 'ERROR - Metal Loading Not Defined'
    ERROR3 = 'ERROR - Metal Center not in Complex'
    ERROR4 = 'ERROR - Support Not Defined'
    
    if Support == '':
        return ERROR4

    elif Complex == '':
        return ERROR1
    
    elif Metal_Loading == '':
        return ERROR2
    
    elif Metal_Site in Complex:
        metal_Loading = float(Metal_Loading)
               
        # Parse metal Site 1 and Support 
        MetalSite_Elements = xraylib.CompoundParser(Complex)
        
        Support_Elements = xraylib.CompoundParser(Support)
    
   
        #Calculate New Nass Fractions
        Updated_MF = []
        
        #Find Metal Site in Complex
        ind = MetalSite_Elements['Elements'].index(xraylib.SymbolToAtomicNumber(Metal_Site))
        wt_Factor = metal_Loading/MetalSite_Elements['massFractions'][ind]
        
        #Weight metal site 1 fractions and store them + atomic number      
        for x in range(0,MetalSite_Elements['nElements']):
            if x == 0:
                Updated_MF = [MetalSite_Elements['Elements'][x], MetalSite_Elements['massFractions'][x]*wt_Factor/100]
            else:
                new_line = [MetalSite_Elements['Elements'][x], MetalSite_Elements['massFractions'][x]*wt_Factor/100]   
                Updated_MF = np.vstack((Updated_MF,new_line))
        
        complex_MF = np.sum(Updated_MF[:,1])
        
        #Add Support Mass Fractions
        for x in range(0,Support_Elements['nElements']):
            new_line = [Support_Elements['Elements'][x], Support_Elements['massFractions'][x]*(1-complex_MF)]   
            Updated_MF = np.vstack((Updated_MF,new_line))
    
        
        #Calcualte Moles of each component
        mol = []
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
            else:
                new_mol = Updated_MF[x,1]/xraylib.AtomicWeight(int(Updated_MF[x,0]))
                mol = np.vstack((mol,new_mol))
        
        mol = mol/min(mol)

       
        #Build New String
        for x in range(0,np.shape(Updated_MF)[0]):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Updated_MF[x,0])), float(mol[x]))
                Sample_String = Sample_String+new_String

        Constructed_Sample = xraylib.CompoundParser(Sample_String)

        
        #Build Condensed String
        for x in range(0,Constructed_Sample['nElements']):
            if x == 0:
                Sample_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x])) 
            else:
                new_String = '{0:s}{1:0.6f}'.format(xraylib.AtomicNumberToSymbol(int(Constructed_Sample['Elements'][x])), float(Constructed_Sample['nAtoms'][x]))
                Sample_String = Sample_String+new_String
        
        return Sample_String
    
    else:
        return ERROR3


# --- kspacecalc: reference lines 4101-4105, verbatim ---
def kspacecalc(EminusEnot):
        import math
        kfromE = math.sqrt((8*math.pi**2*9.10938291*10**-31)/(6.6260695729*10**-34*4.13566751691*10**-15)*(EminusEnot))*1/(10**10)
        
        return kfromE


# --- BeamTrans: reference lines 4108-4121, verbatim ---
def BeamTrans(Sample):
    Sample_Elements = xraylib.CompoundParser(Sample)
    #new_mu = np.multiply(Photo_XS[x,:],Elements['massFractions'][x])
    #mu_tot = np.vstack((mu_tot, new_mu))
    densities =[]
    
    for i in range(0,Sample_Elements['nElements']):
        atomicnumber = Sample_Elements['Elements'][i]
        density = xraylib.ElementDensity(atomicnumber)
        densityfrac = density*Sample_Elements['massFractions'][i]
        densities = np.append(densities,density)
    #sample_density = np.sum(densities) 
    
    return Sample_Elements,densityfrac,densities


# --- XASEZero: reference lines 4123-4157, verbatim ---
def XASEZero(Sample,Enot):
    

    Elements = xraylib.CompoundParser(Sample)
    y = ['K','L1','L2','L3'] # add the other edges if need to y vector
    atomicnumbers=[]
    atomicsymbols=[]
    atomicedges=[]
    atomicedgesymbols=[]
    kspaceedges = []
    k = 0
    
    for i in range(0,Elements['nElements']):
        atomicnumber = Elements['Elements'][i]
        atomicsymbol = xraylib.AtomicNumberToSymbol(atomicnumber)
        for j in range(len(y)):
            try:
                atomicedge = xraylib.EdgeEnergy(atomicnumber,j)*1000-Enot
            except:
                pass
                atomicedge = 0
            
            if atomicedge <=0:
                k = k
            else:
                #kspaceedge = math.sqrt((8*math.pi**2*9.10938291*10**-31)/(6.6260695729*10**-34*4.13566751691*10**-15)*(atomicedge))*1/(10**10)
                kspaceedge = kspacecalc(atomicedge)
                kspaceedges= np.append(kspaceedges, kspaceedge)
                atomicedges = np.append(atomicedges, atomicedge+Enot)
                atomicsymbols = np.append(atomicsymbols, atomicsymbol)
                atomicnumbers = np.append(atomicnumbers, atomicnumber)
                atomicedgesymbols = np.append(atomicedgesymbols, y[j])
            
    
    return kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols


# --- XASEZeroList: reference lines 4159-4187, verbatim ---
def XASEZeroList(Sample):
    

    Elements = xraylib.CompoundParser(Sample)
    y = ['K','L1','L2','L3'] # add the other edges if need to y vector
    atomicnumbers=[]
    atomicsymbols=[]
    atomicedges=[]
    atomicedgesymbols=[]
    k = 0
    
    for i in range(0,Elements['nElements']):
        atomicnumber = Elements['Elements'][i]
        atomicsymbol = xraylib.AtomicNumberToSymbol(atomicnumber)
        for j in range(len(y)):
            try:
                if xraylib.EdgeEnergy(atomicnumber,j)*1000-100 <=0 or xraylib.EdgeEnergy(atomicnumber,j)*1000 <=200:
                    k = k
                else:
                    atomicedge = xraylib.EdgeEnergy(atomicnumber,j)*1000
                    atomicedges = np.append(atomicedges, atomicedge)
                    atomicsymbols = np.append(atomicsymbols, atomicsymbol)
                    atomicnumbers = np.append(atomicnumbers, atomicnumber)
                    atomicedgesymbols = np.append(atomicedgesymbols, y[j])
            except:
                pass
            
    
    return atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols


# --- unitconvert: reference lines 4189-4205, verbatim ---
def unitconvert(thickness,Cindex):
    if Cindex == 0 :
        thickness = float(thickness)*2.54
           
    elif Cindex == 1 :
        thickness = float(thickness)*0.00254
           
    elif Cindex == 2 :
        thickness = float(thickness)
            
    elif Cindex == 3 :
        thickness = float(thickness)*0.1
            
    elif Cindex == 4 :
        thickness = float(thickness)*0.0001
        
    return thickness


# --- ionchamberdensity: reference lines 4208-4214, verbatim ---
def ionchamberdensity(Ptotal,gas1,gas2,molfrac):
    
    formula1,elementdensity1 = xraydb.get_material(gas1)
    formula2,elementdensity2 = xraydb.get_material(gas2)
    densitymix = molfrac*elementdensity1+(1-molfrac)*elementdensity2
    iondensity = Ptotal*densitymix/760
    return iondensity


# =============================================================================================
# 3. Physics lifted out of v3's GUI methods
# =============================================================================================

# --- Sample holder geometry (setarea, reference lines 1254-1296) ------------------------------
def holder_area(holder, capillary_mm='', bed_cm='', pellet_mm='', other_cm2=''):
    """Sample area perpendicular to the beam [cm^2], unrounded.

    holder: 'capillary', 'pellet', or 'other'. Inputs are v3's box strings.
    Capillary: inner diameter [mm] x bed length [cm] / 10, the projected area (full illumination).
    v3 then writes this to the area box as 0.2f text and reads the text back as the calculation
    input (finding 9). Decision 2026-11-08: full precision in Release 1, applied where the new
    UI calls this; the rounding is not reproduced here.
    """
    if holder == 'capillary':
        crossarea = float(capillary_mm)*float(bed_cm)/10
    elif holder == 'pellet':
        crossarea = (math.pi/4)*float(pellet_mm)**2/100
    elif holder == 'other':
        crossarea = float(other_cm2)
    else:
        raise ValueError(f"unknown holder {holder!r}")
    return crossarea


def angle_factor(angle_deg):
    """sin of the sample angle to the beam, as v3 evaluates it (slider value rounded to 1 deg)."""
    return math.sin(round(angle_deg, 0)*2*math.pi/360)


def projected_area(area, angle_deg):
    """Area seen by the beam for a sample tilted to angle_deg (setarea, angle branch)."""
    return float(area)*angle_factor(angle_deg)


def projected_al(AL, angle_deg):
    """Absorption length along the tilted path (setAL / b1_function / valuechange_deg)."""
    return float(AL)/angle_factor(angle_deg)


# --- Main calculation (calculateResult, reference lines 2206-2333) -----------------------------
def calculate_result(Sample, Element, Edge, Area, AL, Sample_DR='', Diluent_DR=''):
    """Mass, edge step and E0 for one "Calculate Sample Mass" click.

    Arguments are the strings v3 reads: diluted formula, element, edge ('K', 'L1'-'L3' or an
    energy in eV), area [cm^2], target absorption length, and the two dilution-ratio boxes.
    Includes v3's edge-step retry loop unchanged (finding 3, Release 2): if the step is <= 0 the
    window shrinks 40, 30, ..., 0 and then goes negative, while mass and E0 stay from the
    first call.

    Returns a dict: Result (error text or 'None'), Enot [eV], ms [mg], stp, muave,
    whilecount, newsetp, MF_Samp, MF_Dil.
    Change F7: invalid non-empty inputs return an 'ERROR - ...' Result instead of raising.
    """
    error = calculation_input_error(Sample, Element, Edge, Area, AL, Sample_DR, Diluent_DR)
    if error:
        return {'Result': error, 'Enot': 0, 'ms': 0, 'stp': 0, 'muave': AL, 'whilecount': 1,
                'newsetp': None, 'MF_Samp': None, 'MF_Dil': None}

    if Sample_DR == '':
        A = 1
    else:
        A = float(Sample_DR)

    if Diluent_DR == '':
        B= 0
    else:
        B = float(Diluent_DR)

    MF_Samp = A/(A+B)
    MF_Dil = 1-MF_Samp

    Result, Enot, ms, stp,muave = XASMassCalc(Sample, Element, Edge, Area, AL)

    # correction when edge step negative due to slope in backgound
    whilecount = 1
    newsetp = None
    while stp<=0 and whilecount<49:
        Result_stp, Enot_stp, ms_stp, stp,muave_stp = XASMassCalc(Sample, Element, Edge, Area, AL,50-10*whilecount,50-10*whilecount)
        whilecount +=1
        newsetp = 50-whilecount

    return {'Result': Result, 'Enot': Enot, 'ms': ms, 'stp': stp, 'muave': muave,
            'whilecount': whilecount, 'newsetp': newsetp, 'MF_Samp': MF_Samp, 'MF_Dil': MF_Dil}


def result_display(r, angle_mode=False):
    """Text v3 writes to the results boxes, or None on an error (v3 leaves them unchanged).

    Keys: mass, step, sample_mass, diluent_mass, E0 (display strings), step_red (the box turns
    red when the step exceeds 1; v3 tests the raw value, or the 4-decimal text in angle mode).
    """
    if 'ERROR' in r['Result']:
        return None
    ms, stp = r['ms'], r['stp']
    shown = {'mass': '{0:0.2f}'.format(ms),
             'step': '{0:0.4f}'.format(stp),
             'sample_mass': '{0:0.2f}'.format(ms*r['MF_Samp']),
             'diluent_mass': '{0:0.2f}'.format(ms*r['MF_Dil']),
             'E0': '{0:0.0f}'.format(r['Enot'])}
    if not angle_mode:
        shown['step_red'] = bool(stp > 1)
    else:
        shown['step_red'] = float(shown['step']) > 1
    return shown


def retry_window(whilecount):
    """Edge-step window [eV] actually used: retry k (k = whilecount - 1) uses 50 - 10k eV."""
    return 50 - 10*(whilecount - 1)


def retry_window_text(whilecount):
    """'E0 ± <window> eV', flagged when the window is zero or reversed (finding 3)."""
    window = retry_window(whilecount)
    text = f'E0 ± {window} eV'
    if window == 0:
        text += ' (no window; step not reliable)'
    elif window < 0:
        text += ' (below/above swapped; step not reliable)'
    return text


def diagnostic_text(r, plot=False, angle_mode=False):
    """The results-panel diagnostic line, in v3's order of overwrites (lines 2256-2333).

    Change F3a (finding 3, note text only; approved 2026-11-08): v3's note gave its loop counter
    (newsetp = 50 - whilecount, e.g. "± 43") instead of the window used (-10 eV in that case).
    The note now states the window used, as the "values used" list does. The retry loop itself
    is unchanged until Release 2 (Upgrade 3).
    """
    Result, whilecount = r['Result'], r['whilecount']
    note = 'Note: Edge step at: ' + retry_window_text(whilecount)
    text = Result if 'ERROR' in Result else ''
    if not plot:
        text = Result
        if whilecount !=1 and not angle_mode:
            text = note + ', consider fluorescence'
        if whilecount !=1 and angle_mode:
            text = note
        if whilecount >=48:
            text = 'Background Level Edge Step'
    if 'ERROR' in Result:
        text = Result
    if plot:
        if whilecount !=1 and not angle_mode:
            text = note + ', consider fluorescence'
        if whilecount !=1 and angle_mode:
            text = note
        if whilecount >=48:
            text = 'Background Level Edge Step'
    return text


# --- Crystal glitch library (calculateResult, STAFF ONLY block, lines 2403-2487) --------------
GLITCH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'glitch')

# (file, legend label, shown by default), in v3's order. v3 hides the Si(111) pair by default.
GLITCH_LIBRARY = [
    ('si2209093.txt', 'Si(220), Φ = 90°', True),
    ('si220093.txt', 'Si(220), Φ = 0°', True),
    ('si1119043.txt', 'Si(111), Φ = 90°', False),
    ('si111043.txt', 'Si(111), Φ = 0°', False),
]


def glitch_overlay(Enot, start, stop, glitch_dir=GLITCH_DIR):
    """Glitch points inside the plot window, in energy and in k, for each library file.

    start/stop: plot window in eV relative to E0 (v3's start and stop = upper + 0.5 eV).
    Returns a list of dicts (file, label, visible, E_x, E_y, k_x, k_y), or None when any file
    cannot be read or parsed. v3 wraps the whole block in one try/except, so the overlay
    disappears entirely in that case.
    Assumption (HC16): the library ships with the package; v3 read the files from the working
    directory, which is why the overlay appeared only for staff.
    """
    try:
        crystals = [open(os.path.join(glitch_dir, f)).read().splitlines()
                    for f, _, _ in GLITCH_LIBRARY]
        parsed = []
        for crystal in crystals:
            crystal_x = []
            crystal_y = []
            for i in range(len(crystal)):
                crystal_x.append(crystal[i].split(" ")[0])
                crystal_y.append(crystal[i].split(" ")[len(crystal[i].split(" "))-1])
            parsed.append((crystal_x, crystal_y))
        overlay = []
        for (fname, label, visible), (crystal_x, crystal_y) in zip(GLITCH_LIBRARY, parsed):
            plot_x, plot_y, k_x, k_y = [], [], [], []
            for i in range(len(crystal_x)):
                if float(start)+Enot<float(crystal_x[i])<=float(stop)+Enot:
                    plot_x.append(float(crystal_x[i]))
                    plot_y.append(float(crystal_y[i]))
                    if Enot<float(crystal_x[i])<=float(stop)+Enot:
                        k_x.append(kspacecalc(float(crystal_x[i])-Enot))
                        k_y.append(float(crystal_y[i]))
            overlay.append({'file': fname, 'label': label, 'visible': visible,
                            'E_x': plot_x, 'E_y': plot_y, 'k_x': k_x, 'k_y': k_y})
        return overlay
    except Exception:
        return None


# --- Plot data (calculateResult plot path, lines 2348-2734) ------------------------------------
def plot_data(Sample, Element, Edge, Area, AL, ms, Enot, lower, upper, glitch_dir=GLITCH_DIR):
    """Everything v3's three-panel plot shows, as data (no plotting library needed).

    Sample..AL: as for calculate_result (in angle mode v3 passes the projected AL as a string);
    ms [mg] and Enot [eV] from calculate_result; lower/upper: plot-limit boxes [eV from E0].

    Panels:
    - energy: total sample absorption mu_ave * mass/area vs. photon energy, plus the estimated
      edge step of every edge of every element in the sample (the all-edges table) at the
      actual sample mass;
    - k: k of the sample's other edges above E0, and the glitch overlay in k;
    - fluorescence: emission lines of every edge of every element, x-range centred on the
      scanned edge's alpha-1 line (or the "Other" energy).
    'error' is None, or an 'ERROR - ...' message for unusable plot limits (then no other keys).
    Change F7: v3 crashed for an "Other" energy with a decimal (int() of the energy text) and for
    non-numeric or reversed plot limits.
    """
    for text, what in ((lower, 'Lower plot limit'), (upper, 'Upper plot limit')):
        if text == '':
            return {'error': f"ERROR - {what} not defined"}
        error = number_error(text, what, minimum=-math.inf)
        if error:
            return {'error': error}
    if float(lower) >= float(upper):
        return {'error': "ERROR - Lower plot limit must be below the upper plot limit"}
    if Enot + float(lower) <= 0:
        return {'error': "ERROR - Lower plot limit reaches below 0 eV photon energy"}

    kspaceedges, atomicedges,atomicsymbols,atomicnumbers,atomicedgesymbols = XASEZero(Sample,Enot)

    atomicedgesall,atomicsymbolsall,atomicnumbersall,atomicedgesymbolsall = XASEZeroList(Sample)

    #ploting limits
    delta1 = float(lower)
    delta2 = float(upper)
    start = delta1
    interval = 0.5
    stop = delta2+interval

    #create vector for x axis of fig 1 and fif 2
    x = np.arange(start, stop, interval)
    x2 = np.arange(1, stop, interval)
    #define how long the vectors are
    length = len(x)
    length2 = len(x2)
    length3 = len(kspaceedges)
    length4 = len(atomicsymbolsall)
    #define blank y values to be populated by later functions
    y  = [None] * length #list of modified muave
    y2  = [None] * length2 #list of zeros fro kspace plot ( should be glitches)
    y3 = [None] * length3 #list of edges from sample

    yedges = [None]* length4
    muaves = [None]*length4 #list of muave for edge label in E plot
    Enots = [None]*length4
    yedges2 = [None]* length4
    Enots2 = [None]*length4
    muaves2 = [None]*length4 #list of muave for edge label in E plot
    kspace  = [None] *length2

    #kpace plot y values for now
    for i in range(length3):
        y3[i]=0
    #kspace  y value points are edges of element in sample that could show up in kspace
    for i in range(length2):
        kspace[i] = kspacecalc(x2[i])

    glitches = glitch_overlay(Enot, start, stop, glitch_dir)

    #plot of modified mu average (Absorption length over energy range)
    for i in range(length):
        y[i] = XASPLOTTER(Sample, Element, Edge, Area, AL, x[i],delta1)
        y[i] =float(y[i])*(ms/float(Area))/1000
    #redefining x axis to absolute scale
    x = np.arange(start, stop, interval)+Enot

    # v3 also builds mass fractions and symbols here (wt, wtelem, wt_sym) but never uses them.
    x_xrayf_lines = []
    y_xrayf_lines = []
    xrayf_lines_name = []
    for i in range(length4):
        for name, line in xraydb.xray_lines(atomicsymbolsall[i], atomicedgesymbolsall[i]).items():
            xrayf_lines_name.append(name + " " + atomicsymbolsall[i] + " " + atomicedgesymbolsall[i])
            x_xrayf_lines.append(line[0])
            y_xrayf_lines.append(line[1])

    energy_xlim = [Enot+delta1, Enot+delta2]
    energy_ylim = [0, max(y)*1.5]
    k_xlim = [0, kspacecalc(delta2)]
    fluorescence_band = None
    try:
        fluorescence_xlim = [x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]-800, x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]+800]
        fluorescence_ylim = [0, max(y_xrayf_lines)*1]
        fluorescence_band = [x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]-250,x_xrayf_lines[xrayf_lines_name.index(Edge[0]+'a1'+' '+Element+' '+Edge)]+250, max(y_xrayf_lines)]
    except:
        # Change F7: v3 used int(Edge) here, which crashed for an "Other" energy with a decimal,
        # for L1/L2 edges (they have no alpha-1 line) and for an element absent from the sample.
        # Now: "Other" -> the energy (as v3); otherwise the strongest emission line of the
        # scanned edge (alpha-1 for K and L3, so v3's choice), or E0 if there is none.
        own = [i for i, n in enumerate(xrayf_lines_name) if n.endswith(' '+Element+' '+Edge)]
        if Edge not in EDGE_SHELLS:
            centre = float(Edge)
        elif own:
            centre = x_xrayf_lines[max(own, key=lambda i: y_xrayf_lines[i])]
            fluorescence_band = [centre-250, centre+250, max(y_xrayf_lines)]
        else:
            centre = Enot
        fluorescence_xlim = [centre-800, centre+800]
        fluorescence_ylim = [0, max(y_xrayf_lines)*1]

    for i in range(length4):
        Result1, Enots[i], ms1, yedges[i],muaves[i] = XASMassCalc(Sample, atomicsymbolsall[i], atomicedgesymbolsall[i], Area, AL)
        muaves[i] =float(muaves[i])*(ms/float(Area))/1000
        Result2, Enots2[i], ms1, yedges2[i],muaves2[i] = XASMassCalc(Sample, atomicsymbolsall[i], Enots[i], Area, muaves[i])
        yedges[i]='{0:0.3f}'.format(yedges2[i])

    return {
        'error': None,
        'energy': {'x': x, 'y': y, 'xlim': energy_xlim, 'ylim': energy_ylim,
                   'edges_E': Enots, 'edges_absorption': muaves, 'edges_step_label': yedges,
                   # which edge each entry is (for labels and export; v3 did not show these)
                   'edges_element': [str(s) for s in atomicsymbolsall],
                   'edges_shell': [str(s) for s in atomicedgesymbolsall]},
        'k': {'x': kspace, 'y': y2, 'xlim': k_xlim,
              'edges_k': kspaceedges, 'edges_y': y3,
              'edge_labels': list(atomicedgesymbols), 'element_labels': list(atomicsymbols)},
        'fluorescence': {'x': x_xrayf_lines, 'y': y_xrayf_lines, 'names': xrayf_lines_name,
                         'xlim': fluorescence_xlim, 'ylim': fluorescence_ylim,
                         'band': fluorescence_band},
        'glitches': glitches,
    }


# --- Beam-path panel (Calculatetransbeam / Calculateabsbeam_materials, lines 2866-2927) -------
def transmission_panel(Enot, gas, gas_thickness, gas_unit, material, material_thickness,
                       material_unit, solvent, solvent_thickness, solvent_unit, metal,
                       metal_thickness, metal_unit, absorbed=False):
    """'% Transmitted' (or 'Beam Absorbed (µx)' if absorbed) at E0 + 50 eV for each panel row.

    Enot: the E0 results box text (whole eV). Units: v3 combo indices (0 in, 1 mils, 2 cm,
    3 mm, 4 um). Returns {row: display text} for rows with a thickness.
    Change F1 (finding 1, approved 2026-11-08): each row uses its own material. v3 computed the
    solvent row with the gas dropdown's material and the metal row with the solvent dropdown's.
    Change F7: a non-numeric or negative thickness, or no E0 yet, gives an 'ERROR - ...' text for
    that row (v3 crashed).
    """
    Materialgases = gas
    Materialwall = material
    Materialsolvent = solvent  # v3: self.combo3 (gas dropdown); change F1
    Materialmetal = metal      # v3: self.combo4 (solvent dropdown); change F1
    shown = {}
    rows = [('gas', gas_thickness, gas_unit, Materialgases),
            ('material', material_thickness, material_unit, Materialwall),
            ('solvent', solvent_thickness, solvent_unit, Materialsolvent),
            ('metal', metal_thickness, metal_unit, Materialmetal)]
    for row, thickness, unit, mat in rows:
        if thickness !='':
            error = number_error(thickness, f"{row.capitalize()} thickness", allow_minimum=True)
            if Enot == '':
                error = "ERROR - E0 not defined; calculate the sample mass first"
            if error:
                shown[row] = error
                continue
            thickness = unitconvert(thickness,unit)
            trans = np.exp(-float(thickness) *  xraydb.material_mu(mat,float(Enot)+50))*100
            if absorbed:
                shown[row] = '{0:0.1f}'.format(-np.log(trans/100))
            else:
                shown[row] = '{0:0.1f}'.format(trans)+ '%'
    return shown


# --- Ion chambers (CalBeamabs, lines 2930-2950) -----------------------------------------------
def ion_chamber_absorbed(Enot, gas1, gas2, gas1_slider, pressure_torr, length, other_length=''):
    """'% Beam Absorbed' text for the ion-chamber calculator at E0.

    Enot: E0 results box text ('' gives v3's "Error"). gas1_slider: v3 slider value, -100..0
    (gas 1 fraction = -value/100). pressure_torr: total pressure slider. length: '10', '15',
    '30', '45', '60' [cm] or 'Other', with other_length the typed length (blank: v3 leaves the
    box unchanged, returned as None).
    Change F2 (finding 2, approved 2026-11-08): each gas is taken at its own partial density,
    mole fraction x density at 1 atm x P/760 (ideal gas), as xraydb's ionchamber_fluxes mixes
    gases. v3 applied the mixture's average density to both gases (via ionchamberdensity), which
    is exact only for a single gas and under-counts the denser gas in a mix.
    Assumption (HC16, as in v3): the slider fraction is a mole (pressure) fraction.
    """
    if Enot=='':
        return "Error"
    if length == 'Other':
        if other_length =='':
            return None
        error = number_error(other_length, 'Ion chamber length')  # change F7
        if error:
            return error
        L = other_length
    else:
        L = length
    pressure_scale = pressure_torr/760
    density1 = xraydb.get_material(gas1)[1]*pressure_scale
    density2 = xraydb.get_material(gas2)[1]*pressure_scale
    ionchambergas1 =  -gas1_slider/100*float(L)*xraydb.material_mu(gas1,float(Enot),density=density1)
    ionchambergas2 =  (100+gas1_slider)/100*float(L)*xraydb.material_mu(gas2,float(Enot),density=density2)
    transionchamber = np.exp(-(ionchambergas1+ionchambergas2))*100
    return '{0:0.2f}'.format(100-transionchamber)


# --- Sample Builder, complexes tab (UpdateSampleComplex, lines 3276-3324) ---------------------
def build_complex_sample(Support, Complex, Complex_Loading, Metal_Loading, Metal_Center):
    """Formula for a supported complex, or v3's message text.

    Complex loading only: treated as a metal site of that loading (metalCalculateSample).
    Metal loading + metal center: ComplexCalculateSample. Anything else: v3's message.
    Change F7: invalid inputs return an 'ERROR - ...' message instead of raising.
    """
    error = complex_input_error(Support, Complex, Complex_Loading, Metal_Loading, Metal_Center)
    if error:
        return error
    if Complex_Loading != '' and Metal_Loading == '':
        return metalCalculateSample(Complex, Complex_Loading, '', '', Support)
    elif Complex_Loading == '' and Metal_Loading != '' and Metal_Center != '':
        return ComplexCalculateSample(Complex, Metal_Loading, Metal_Center, Support)
    else:
        return 'COMPLEX LODAING/METAL LOADING/METAL CENTER INCORRECTLY DEFINED'


# =============================================================================================
# 4. Input validation (change F7)
# =============================================================================================
# Decision 2026-11-08 (finding 7): invalid input is caught here, in the physics layer, and
# returned as an 'ERROR - ...' message in v3's convention; the UI only displays it. Empty fields
# are left to v3's own messages (and to the UI defaults agreed for Release 1). Valid input reaches
# the v3 functions unchanged, so every golden value still holds.

# Lowest edge or "Other" energy accepted (researcher decision 2026-11-08): 2000 eV, which still
# covers S K (2472 eV). Below that nearly everything absorbs too strongly for this calculation
# to be useful. v3 accepted lower energies, and crashed below about 430 eV (its retry loop
# evaluates down to E0 - 430 eV; xraylib rejects energies <= 0).
MIN_EDGE_ENERGY_EV = 2000

EDGE_SHELLS = {'K': 0, 'L1': 1, 'L2': 2, 'L3': 3}


def formula_error(text, what):
    """Message if a non-empty formula cannot be parsed, else None."""
    if text == '':
        return None
    try:
        xraylib.CompoundParser(text)
    except ValueError as exc:
        reason = str(exc).replace('Invalid chemical formula: ', '')
        return (f"ERROR - {what} '{text}' is not a valid chemical formula ({reason}). "
                "Element symbols are case-sensitive, e.g. Al2O3")
    return None


def element_error(text, what):
    """Message if a non-empty element symbol is not an element, else None."""
    if text == '':
        return None
    try:
        xraylib.SymbolToAtomicNumber(text)
    except ValueError:
        return (f"ERROR - {what} '{text}' is not an element symbol. "
                "Symbols are case-sensitive, e.g. Fe")
    return None


def number_error(text, what, minimum=0.0, allow_minimum=False, below=None):
    """Message if a non-empty number box is not a number in range, else None.

    Accepts values > minimum (or >= minimum if allow_minimum) and, if given, < below.
    """
    if text == '':
        return None
    try:
        value = float(text)
    except (TypeError, ValueError):
        return f"ERROR - {what} '{text}' is not a number"
    if not math.isfinite(value):
        return f"ERROR - {what} '{text}' is not a finite number"
    if value < minimum or (value == minimum and not allow_minimum):
        bound = 'at least' if allow_minimum else 'greater than'
        return f"ERROR - {what} must be {bound} {minimum:g}"
    if below is not None and value >= below:
        return f"ERROR - {what} must be less than {below:g}"
    return None


def calculation_input_error(Sample, Element, Edge, Area, AL, Sample_DR='', Diluent_DR=''):
    """First problem with the inputs of calculate_result, or None."""
    error = formula_error(Sample, 'Sample')
    if error:
        return error
    if Edge in EDGE_SHELLS:
        error = element_error(Element, 'Element to be Scanned')
        if error:
            return error
        if Element != '':
            try:
                E0 = xraylib.EdgeEnergy(xraylib.SymbolToAtomicNumber(Element), EDGE_SHELLS[Edge])
            except ValueError:
                return f"ERROR - {Element} has no {Edge} edge"
            if E0*1000 < MIN_EDGE_ENERGY_EV:
                return (f"ERROR - {Element} {Edge} edge ({E0*1000:.0f} eV) is below the "
                        f"{MIN_EDGE_ENERGY_EV} eV minimum")
    else:
        if Edge == '':  # v3 crashed here (float('') of the "Other" energy box)
            return 'ERROR - Energy to calculate sample mass not Defined'
        error = number_error(Edge, 'Energy to calculate sample mass', minimum=MIN_EDGE_ENERGY_EV,
                             allow_minimum=True)
        if error:
            return error + ' eV' if 'must be' in error else error
    for text, what in ((Area, 'Sample area'), (AL, 'Absorption length')):
        error = number_error(text, what)
        if error:
            return error
    error = number_error(Sample_DR, 'Sample ratio')
    if error:
        return error
    return number_error(Diluent_DR, 'Diluent ratio', allow_minimum=True)


def dilute_sample(Sample, Diluent, Sample_DR, Diluent_DR):
    """XASStoichCalc with input validation: (error message or 'None', diluted formula)."""
    for error in (formula_error(Sample, 'Sample'), formula_error(Diluent, 'Diluent'),
                  number_error(Sample_DR, 'Sample ratio'),
                  number_error(Diluent_DR, 'Diluent ratio', allow_minimum=True)):
        if error:
            return error, ''
    return XASStoichCalc(Sample, Diluent, Sample_DR, Diluent_DR)


def build_metal_sample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support):
    """metalCalculateSample (Sample Builder, metals tab) with input validation."""
    for error in (formula_error(Support, 'Support'), formula_error(Metal_Site1, 'Metal site 1'),
                  formula_error(Metal_Site2, 'Metal site 2'),
                  number_error(Metal1_Loading, 'Metal site 1 loading [wt%]', below=100),
                  number_error(Metal2_Loading, 'Metal site 2 loading [wt%]', below=100)):
        if error:
            return error
    if Metal1_Loading != '' and Metal_Site2 != '' and Metal2_Loading != '':
        total = float(Metal1_Loading) + float(Metal2_Loading)
        if total >= 100:
            return f"ERROR - Metal loadings add up to {total:g} wt%; they must total less than 100 wt%"
    return metalCalculateSample(Metal_Site1, Metal1_Loading, Metal_Site2, Metal2_Loading, Support)


def complex_input_error(Support, Complex, Complex_Loading, Metal_Loading, Metal_Center):
    """First problem with the Sample Builder complexes-tab inputs, or None."""
    for error in (formula_error(Support, 'Support'), formula_error(Complex, 'Metal complex'),
                  number_error(Complex_Loading, 'Complex loading [wt%]', below=100),
                  number_error(Metal_Loading, 'Metal loading [wt%]', below=100),
                  element_error(Metal_Center, 'Metal center')):
        if error:
            return error
    if Complex != '' and Metal_Loading != '' and Metal_Center != '' and Complex_Loading == '':
        parsed = xraylib.CompoundParser(Complex)
        Z = xraylib.SymbolToAtomicNumber(Metal_Center)
        if Z not in parsed['Elements']:
            return 'ERROR - Metal Center not in Complex'  # v3's message (ERROR3)
        fraction = parsed['massFractions'][parsed['Elements'].index(Z)]
        complex_wt = float(Metal_Loading)/fraction
        if complex_wt >= 100:
            return (f"ERROR - {Metal_Loading} wt% {Metal_Center} needs {complex_wt:.1f} wt% of "
                    "this complex; it must be less than 100 wt%")
    return None
