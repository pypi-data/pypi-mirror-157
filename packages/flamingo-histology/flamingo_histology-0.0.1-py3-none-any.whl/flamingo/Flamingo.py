'''
Flamingo

Scope:

Usage:

'''

import os
import sys
import xml
#import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImagePath
import openslide
import json


class HE:
    '''
    HE: Load .ndpi files and annotations for conversion and output.
    '''
    
    def __init__(self,path,name,resolution=None):
        '''
        Initialise object with file path and name.
        '''
        # __init__ Initialise class and run basic functions
    
        # Check if files and annotations exist
        assert name[-4:] == 'ndpi', 'Please provide a Hammamatsu file with extension *.ndpi.'
        assert os.path.exists(path+name), '.ndpi file not found.'
        assert os.path.exists(path+name+'.ndpa'), 'No annotation file .ndpa file found.'
        
        # Save all information
        self.path = path
        self.name = name
        self.ndpa = name + '.ndpa'
        self.anno = None
        
        # Run initialisation functions
        self.imageProperties()
        self.annotationImport()
        
        # If resolution of the low res image has been provided, perform the following
        # methods automatically
        if resolution is not None:
            
            # Get low resolution image
            self.imageLoRes(resolution=resolution)
            
            # Convert annotations to image matching low res
            self.annotationMask()
                
        
        
    def __str__(self):
        
        msg1 = 'File: %s.' % self.name
        
        if self.anno is not None:
            msg2 = '\nAnnotation labels:'
            for a in self.anno:
                msg3 = ' %s;' % a[0]
                msg2 = msg2 + msg3
        else:
            msg = '\nNo annotations extracted.'
        
        return msg1+msg2
    
    
    def imageProperties(self):
        '''
        Determine relevant properties of the image.
        '''
        
        # imageProperties Read .ndpi parameters required for conversion of annotations
        
        # Openslide image handle
        self.he = openslide.OpenSlide(self.path+self.name)
        
        # Full size image dimensions
        self.dim = self.he.dimensions
        
        # These are the properties which are required
        props = self.he.properties
        self.xoffset = float(props['hamamatsu.XOffsetFromSlideCentre'])
        self.yoffset = float(props['hamamatsu.YOffsetFromSlideCentre'])
        self.xmpp    = float(props['openslide.mpp-x'])
        self.ympp    = float(props['openslide.mpp-y'])
        
        
    def annotationImport(self):
        '''
        Import annotations from the XML-formatted file.
        '''
        # importAnnotations Read the XML-formatted .ndpa file
        
        # Parse the annotation file
        tree = xml.etree.ElementTree.parse(self.path+self.ndpa)
        root = tree.getroot()
        
        # Empty storage
        anno = []
        
        # Loop through each child of the root
        for child1 in root:
            for child2 in child1:

                # Get the text label
                if child2.tag == 'title':
                    annoText = child2.text
                    #print(annoText)

                # Loop through
                for child3 in child2:

                    if child3.tag == 'pointlist':
                        xy = np.zeros((len(child3),2))
                        for i,child4 in enumerate(child3):
                            xy[i,:] = [child4[0].text,child4[1].text]

                        # Convert... subtract offset; divide by nanometers per pixel; add half 
                        # image dimensions to remove from centred offset
                        xy[:,0] = ((xy[:,0] - self.xoffset) / (self.xmpp * 1000)) + (self.dim[0] / 2)
                        xy[:,1] = ((xy[:,1] - self.yoffset) / (self.ympp * 1000)) + (self.dim[1] / 2)

                        # Save?
                        anno.append((annoText,xy))

        # These are the raw annotations in nanonmeters
        self.anno = anno
        
        
             
    def imageLoRes(self,resolution=2000):
        '''
        Extract low resolution (thumbnail) image
        
        Parameters
            resolution (int): largest of the two dimensions of the thumbnail image
            
        '''
        
        # Save the resolution
        self.lores = resolution
        
        # Get lo res image using Openslide
        self.image = self.he.get_thumbnail((self.lores,self.lores))
        
        # Determine the scaling factor between the thumbnail and the full size image
        sizeImage = np.shape(self.image)
        sizeImage = [sizeImage[1],sizeImage[0]]
        self.scaleFactor = np.mean(np.divide(self.dim,sizeImage))
        
        
    def annotationMask(self):
        '''
        Convert annotations to an image matching low res image size
        '''
        
        # Expect low res image here
        assert hasattr(self,'image'), 'No low res image has been determined. Run imageLoRes() first.'
        
        # Empty image matching lores size
        final = np.zeros((np.shape(self.image)[0], np.shape(self.image)[1]))
        
        # Count up annotations in individual pixels to ensure that pixels arent double counted
        count = np.zeros((np.shape(self.image)[0], np.shape(self.image)[1]))

        # Loop through each annotation
        for i,(txt,xy) in enumerate(self.anno):
    
            # Convert to format required for Image function
            xy = np.round(np.divide(self.anno[i][1],self.scaleFactor)).astype('int')
            pgon = list(map(tuple,xy))
            
            # Create image
            tmp = Image.new('L', (np.shape(self.image)[1], np.shape(self.image)[0]), 0)
            ImageDraw.Draw(tmp).polygon(pgon, outline=1, fill=1)

            # Add to final image (convert to array)
            final = final + (np.array(tmp) * (i+1))
        
        # Remove pixels which are double counted    
        mask = count > 1
        final[mask] = 0
        
        # Save
        self.mask = final
        
        
    def annotationsXY(self):
        '''
        Scale annotations to match the low res image resolution. These are exported as a list array
        rather than stored in the instance.
        '''
        
        scaled = []
        for i,(txt,xy) in enumerate(self.anno):
            
            xy = np.round(np.divide(self.anno[i][1],self.scaleFactor)).astype('int')
            
            scaled.append((txt,xy))
            
        return scaled
        
        
    def annotationPlot(self,type='scatter'):
        '''
        Plot image and/or annotations.
        
        Parameters:
            type (string):  'scatter': raw annotations as a scatter plot
                            'image':   low resolution image only 
                            'combined' overlay scatter annotations on low res image
                            'anno'     low res image and annotation image
        '''
        
        if type == 'anno':
            subPlots = 2
        else:
            subPlots = 1
        
        fig,ax = plt.subplots(ncols=subPlots,figsize=(14,8))
        
        if type == 'scatter':
            
            for txt,xy in self.anno:
                ax.plot(xy[:,0],-xy[:,1],label=txt)
                
        elif type == 'image':
            ax.imshow(self.image)
        
        elif type == 'combined':
            assert hasattr(self,'image'), 'Low resolution image not calculated; use imageLoRes() method first.'
            
            # Plot the image
            ax.imshow(self.image,aspect='auto')
            
            # Plot the annotations
            for txt,xy in self.anno:
                ax.scatter(xy[:,0]/self.scaleFactor,xy[:,1]/self.scaleFactor,label=txt)
                
        elif type == 'anno':
            assert hasattr(self,'mask'), 'Must convert annotations to low res image first with annotationMask().'
            
            ax[0].imshow(self.image)
            ax[1].imshow(self.mask)


        
    def export(self,type='json',path=None):
        '''
        Save annotations/low res image to file.
        
        Parameters:
            type (string): 'json':  coordinates scaled to low res image
                           'mask':  image of coordinates
                           'image': low resolution image
                           'all':   export both
                            
            path (string): valid directory in which to save the results. File name is fixed.
                           If left empty then .ndpi path is used.
        '''
        
        # Where to save?
        if path is None:
            path = self.path
        
        # Type of export
        if type == 'json':
            
            # Export to JSON
            self.exportJSON(path)
            
        elif type == 'mask':
            
            # Export image
            self.exportMask(path)
            
        elif type == 'image':
            
            # Export low res image
            self.exportImage(self,path)
            
        elif type == 'all':
            
            # Export all formats
            self.exportJSON(path)
            self.exportMask(path)
            self.exportImage(path)
            
            
    def exportJSON(self,path):
        '''
        Method to export .json file. Provide save path.
        '''
        
        # Convert annotations to dict for output...
        coord = []
        for lab,xy in self.annotationsXY():

            tmp = {'label': lab,
                  'xy': xy.tolist()}

            coord.append(tmp)
            
        # Now write the json with other parameters
        opdict = {
            'path': self.path,
            'name': self.name,
            'size': np.shape(self.mask),
            'anno': coord
        }
        
        # Write
        with open(path+self.name[0:-5]+'.json', 'w') as outfile:
            json.dump(opdict, outfile)
            
        
    def exportImage(self,path):
        '''
        Method to export low res image. Provide save path.
        '''
        
        # Export low resolution image
        self.image.save(path+self.name[0:-5]+'.jpeg',format='jpeg')
        
        
    def exportMask(self,path):
        '''
        Method to export image mask. Provide save path.
        '''

        # Export as CSV file, despite the size
        np.savetxt(path+self.name[0:-5]+'.csv',self.mask,fmt='%d',delimiter=',')

        