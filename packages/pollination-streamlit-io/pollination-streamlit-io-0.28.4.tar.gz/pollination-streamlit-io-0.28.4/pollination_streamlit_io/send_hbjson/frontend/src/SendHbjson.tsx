import React, { useEffect } from "react"

import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"

import { SendModel } from 'pollination-react-io'

const HEIGHT = 184

/**
 * SendHbjson renders a button that onClick sends geometry from Streamlit to a CAD Platform.
 * It also renders options to continually send new geometry from Streamlit to the CAD platform, and to preview instead of "bake" that geometry.
 * 
 * in via renderData:
 *   hbjson: dictionary
 * 
 * out via Streamlit.setComponentValue
 *
 */
 const SendHbjson: React.VFC = () => {
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
      <SendModel hbjson={renderData && renderData.args && renderData.args['hbjson'] ? renderData.args['hbjson'] : undefined} />
    </div>
  )
}


export default SendHbjson