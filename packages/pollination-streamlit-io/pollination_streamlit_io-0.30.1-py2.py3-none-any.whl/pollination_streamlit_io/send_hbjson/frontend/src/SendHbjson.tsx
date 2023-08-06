import React from "react"

import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"

import { SendModel } from 'pollination-react-io'

const HEIGHT = 184

/**
 * SendHbjson renders a button that onClick sends geometry from Streamlit to a CAD Platform.
 * It also renders options to continually send new geometry from Streamlit to the CAD platform, and to preview instead of "bake" that geometry.
 * 
 * in via renderData:
 *    key: string
 *    hbjson: dictionary
 *    option: string
 * 
 * out via Streamlit.setComponentValue
 *
 */
 const SendHbjson: React.VFC = () => {
  // "useRenderData" returns the renderData passed from Python.
  const renderData: { [index: string]: any }  = useRenderData()

  Streamlit.setFrameHeight(HEIGHT)

  return (
    <div style={{
      height: HEIGHT,
      minHeight: HEIGHT,
      padding: 4
    }}>
      <SendModel 
        hbjson={renderData && renderData.args && renderData.args['hbjson'] ? renderData.args['hbjson'] : undefined} 
        defaultKey={renderData && renderData.args && renderData.args['key'] ? renderData.args['key'] : undefined}
        defaultAction={renderData && renderData.args && renderData.args['option'] ? renderData.args['option'] : undefined}
      />
    </div>
  )
}


export default SendHbjson