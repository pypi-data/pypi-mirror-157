'''
Flamingo

v0.0.1 - Basic package
v0.0.2 - Updated to include circlular annotations


'''

import os
import sys
import xml
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
        
        Parameters:
            path (string)    : folder in which file is stored
            name (string)    : name of file
            resolution (int) : size of low resolution image
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
        '''
        Print quick summary of the instance.
        '''
        
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
        
        tree = xml.etree.ElementTree.parse(self.path+self.ndpa)
        root = tree.getroot()

        # Empty storage
        anno = []
        
        # Loop through the branches of xml file
        for i,annotation in enumerate(root):
            for j,annoInfo in enumerate(annotation):
                if annoInfo.tag == 'title':
                    annoTitle = annoInfo.text
                elif annoInfo.tag == 'annotation':
                    
                    # Now loop through the parts of this annotation to get the 
                    # type and coordinates

                    # Get the type/displayname
                    annoType1 = annoInfo.get('type')
                    annoType2 = annoInfo.get('displayname')

                    # Circles/freehands/arrows/rulers all different
                    if annoType1 == 'freehand':
                        for k,annoList in enumerate(annoInfo):
                    
                            if annoList.tag == 'pointlist':
                                xy = np.zeros((len(annoList),2))

                                for i,annoXY in enumerate(annoList):
                                    xy[i,:] = [annoXY[0].text,annoXY[1].text]

                                # Now convert to pixels rather than nanometers
                                xy[:,0] = ((xy[:,0] - self.xoffset) / (self.xmpp * 1000)) + (self.dim[0] / 2)
                                xy[:,1] = ((xy[:,1] - self.yoffset) / (self.ympp * 1000)) + (self.dim[1] / 2)

                    elif annoType1 == 'circle':

                        xy = np.zeros(3);

                        # Read in xyr and convert to pixel units
                        for k,annoList in enumerate(annoInfo):
                            if annoList.tag == 'x':
                                xy[0] = float(annoList.text)
                                xy[0] = ((xy[0] - self.xoffset) / (self.xmpp * 1000)) + (self.dim[0] / 2)
                            elif annoList.tag == 'y':
                                xy[1] = float(annoList.text)
                                xy[1] = ((xy[1] - self.yoffset) / (self.ympp * 1000)) + (self.dim[1] / 2)
                            elif annoList.tag == 'radius':
                                xy[2] = float(annoList.text)
                                xy[2] = xy[2] / (self.xmpp * 1000) # what if ympp is different?


                    #elif annoType == 'pointer':
                    #elif annoType == 'pin':
                    #elif annoType = 'linearmeasure':

                    
                    else:
                        xy = []
                        msg = '%s: this annotation type is not yet supported.' % (annoType1)
                        print(msg)
                    
                    # Append results to final output
                    if len(xy) != 0:
                        anno.append((annoTitle,annoType1,xy))
        
        # Add to object
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
        
    def circle2mask(self,sxy,cxy,cr):
        '''
        Convert a circle with x,y,r into an image mask
        
        sxy = size image xy
        cxy = center cirle xy
        cr  = circle radius
        '''


        Y, X = np.ogrid[:sxy[0],:sxy[1]]

        dist_from_center = np.sqrt((X - cxy[0])**2 + (Y-cxy[1])**2)

        mask = dist_from_center <= cr
        
        return mask    

    
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
        for i,(txt,annoType,xy) in enumerate(self.anno):
    
            
            if annoType == 'freehand':
                # Convert to format required for Image function
                xy = np.round(np.divide(xy,self.scaleFactor)).astype('int')
                pgon = list(map(tuple,xy))

                # Create image
                tmp = Image.new('L', (np.shape(self.image)[1], np.shape(self.image)[0]), 0)
                ImageDraw.Draw(tmp).polygon(pgon, outline=1, fill=1)
                
            elif annoType == 'circle':
                # Convert circle to mask
                tmp = self.circle2mask(np.shape(self.image),
                                       np.divide([xy[0],xy[1]],self.scaleFactor),
                                       xy[2]/self.scaleFactor)
                
            # Add to final image (convert to array)
            final = final + (np.array(tmp) * (i+1))
            count = count + tmp
        
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
        for i,(txt,annoType,xy) in enumerate(self.anno):
            
            xy = np.round(np.divide(xy,self.scaleFactor)).astype('int')
            
            scaled.append((txt,annoType,xy))
            
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
            
            for txt,annoType,xy in self.anno:
                if annoType == 'freehand':
                    ax.plot(xy[:,0],-xy[:,1],label=txt)
                elif annoType == 'circle':
                    ax.scatter(xy[0],-xy[1],label=txt)
                    ax.scatter(xy[0]+xy[2],-xy[1],label=txt)
                
        elif type == 'image':
            ax.imshow(self.image)
        
        elif type == 'combined':
            assert hasattr(self,'image'), 'Low resolution image not calculated; use imageLoRes() method first.'
            
            # Plot the image
            ax.imshow(self.image,aspect='auto')
            
            # Plot the annotations
            for txt,annoType,xy in self.anno:
                
                if annoType == 'freehand':
                    ax.scatter(xy[:,0]/self.scaleFactor,xy[:,1]/self.scaleFactor,label=txt)
                elif annoType == 'circle':
                    ax.scatter(xy[0]/self.scaleFactor,xy[1]/self.scaleFactor,label=txt)
                    ax.scatter((xy[0]+xy[2])/self.scaleFactor,xy[1]/self.scaleFactor,label=txt)
                    
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
        for lab,annoType,xy in self.annotationsXY():

            tmp = {'label': lab,
                   'type': annoType,
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

        