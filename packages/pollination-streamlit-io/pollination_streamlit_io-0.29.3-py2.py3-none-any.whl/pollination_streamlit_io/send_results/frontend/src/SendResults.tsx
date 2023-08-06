import React, { useEffect } from "react"

import { Streamlit } from "streamlit-component-lib"
import { useRenderData } from "streamlit-component-lib-react-hooks"
import { SendResults } from "pollination-react-io"

/**
 * GetGeometry renders a button that onClick returns an hbjson model from a CAD platform to Streamlit.
 * It also renders a checkbox that can be used subscribe to changes in the hbjson model from the CAD platform. 
 * 
 * in via renderData:
 * 
 * out via Streamlit.setComponentValue
 *   host: string 
 */
const SendResultsSt: React.VFC = () => {

  const renderData: { [index: string]: any }  = useRenderData()

  return (
    <div style={{
      padding: 4
    }}>
    <SendResults
      geometry={renderData && renderData.args && renderData.args['geometry']}
      key={renderData && renderData.args && renderData.args['key']}
    />
    </div>
  )
}

export default SendResultsSt
