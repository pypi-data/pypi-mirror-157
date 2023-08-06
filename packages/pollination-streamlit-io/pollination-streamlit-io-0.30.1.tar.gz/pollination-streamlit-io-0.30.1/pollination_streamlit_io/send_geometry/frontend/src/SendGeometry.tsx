import React from "react"

import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"

import { SendGeometry as SendGeometryComponent } from "pollination-react-io"

const HEIGHT = 184

/**
 * SendGeometry renders a button that onClick sends geometry from Streamlit to a CAD Platform.
 * It also renders options to continually send new geometry from Streamlit to the CAD platform, and to preview instead of "bake" that geometry.
 * 
 * in via renderData:
 *    key: string
 *    geometry: dictionary
 *    option: string
 * 
 * out via Streamlit.setComponentValue
 *
 */
 const SendGeometry: React.VFC = () => {
  // "useRenderData" returns the renderData passed from Python.
  const renderData: { [index: string]: any }  = useRenderData()
  const theme = renderData.theme

  Streamlit.setFrameHeight(HEIGHT)

  return (
    <div style={{
      height: HEIGHT,
      minHeight: HEIGHT,
      padding: 4
    }}>
      <SendGeometryComponent 
        geometry={renderData && renderData.args && renderData.args['geometry'] ? renderData.args['geometry'] : undefined} 
        defaultKey={renderData && renderData.args && renderData.args['key'] ? renderData.args['key'] : undefined}
        defaultAction={renderData && renderData.args && renderData.args['option'] ? renderData.args['option'] : undefined}
      />
    </div>
  )
}


export default SendGeometry