import React, {useState} from 'react';
import TagsInput from 'react-tagsinput';
import 'react-tagsinput/react-tagsinput.css';
import Dropzone from 'react-dropzone'


const CreateProduct = (props) => {
    console.log(props);

    const [productVariantPrices, setProductVariantPrices] = useState([])
    const [url, setUrl] = useState('/product/create-product/')
    const [productVariants, setProductVariant] = useState([
        {
            option: 1,
            tags: []
        }
    ])
    const [productName, setProductName] = useState('')
    const [productSku, setProductSku] = useState('')
    const [productDescription, setProductDescription] = useState('')
    const [productMedia, setProductMedia] = useState([])

    // handle click event of the Add button
    const handleAddClick = () => {
        let all_variants = JSON.parse(props.variants.replaceAll("'", '"')).map(el => el.id)
        let selected_variants = productVariants.map(el => el.option);
        let available_variants = all_variants.filter(entry1 => !selected_variants.some(entry2 => entry1 == entry2))
        setProductVariant([...productVariants, {
            option: available_variants[0],
            tags: []
        }])
    };

    // handle input change on tag input
    const handleInputTagOnChange = (value, index) => {
        let product_variants = [...productVariants]
        product_variants[index].tags = value
        setProductVariant(product_variants)

        checkVariant()
    }

    // remove product variant
    const removeProductVariant = (index) => {
        let product_variants = [...productVariants]
        product_variants.splice(index, 1)
        setProductVariant(product_variants)
    }

    // check the variant and render all the combination
    const checkVariant = () => {
        //alert('check variant')
        let tags = [];

        productVariants.filter((item) => {
            tags.push(item.tags)
        })

        setProductVariantPrices([])

        getCombn(tags).forEach(item => {
            setProductVariantPrices(productVariantPrice => [...productVariantPrice, {
                title: item,
                price: 0,
                stock: 0
            }])
        })

    }

    // combination algorithm
    function getCombn(arr, pre) {
        pre = pre || '';
        if (!arr.length) {
            return pre;
        }
        let ans = arr[0].reduce(function (ans, value) {
            return ans.concat(getCombn(arr.slice(1), pre + value + '/'));
        }, []);
        return ans;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');

    function getBase64(file) {
        return new Promise((resolve, reject) => {
          const reader = new FileReader();
          reader.readAsDataURL(file);
          reader.onload = () => resolve(reader.result);
          reader.onerror = error => reject(error);
        });
      }

    // Save product
    let saveProduct = (event) => {
        event.preventDefault();
        // TODO : write your code here to save the product

        let formData = new FormData();
        formData.append('name', productName);
        formData.append('sku', productSku);
        formData.append('description', productDescription);
        formData.append('variants', JSON.stringify(productVariantPrices));
        formData.append('media', JSON.stringify(productMedia));

        fetch(url, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken,
            }
        }).then(response => response.json())
            .then(result => {
                alert(result.message)
                if (result.success === true){
                    // reload the page
                    window.location.reload()
                } 
                    
            }
        ).catch((error) => {
            console.error('Error:', error);
        });
    }

    const handlePriceOnChange = (event, index) => {
        let product_variant_prices = [...productVariantPrices]
        product_variant_prices[index].price = event.target.value
        setProductVariantPrices(product_variant_prices)
    }

    const handleStockOnChange = (event, index) => {
        let product_variant_prices = [...productVariantPrices]
        product_variant_prices[index].stock = event.target.value
        setProductVariantPrices(product_variant_prices)
    }

    React.useEffect(() => {
        if (props.edit){
            setUrl(`/product/edit-product/${props.edit}/`)
            const product = JSON.parse(props.productobj.replaceAll("'", '"'))
            setProductName(product.title)
            setProductSku(product.sku)
            setProductDescription(product.description)

            let media = []
            let media_list = JSON.parse(props.productimages.replaceAll("'", '"'))
            media_list.forEach((item) => {
                media.push(item.file_path)
            })
            setProductMedia(media)

            let productvariants = []
            let productvariants_list = JSON.parse(props.productvariants.replaceAll("'", '"'))
            productvariants_list.forEach((item) => {
                productvariants.push({
                    id: item.id,
                    variant_title: item.variant_title,
                })
            })

            let productvariantprices = []
            let productvariantprices_list = JSON.parse(props.productvariantprices.replaceAll("'", '"'))
            productvariantprices_list.forEach((item) => {
                const variant_title = productvariants.filter((variant) => variant.id === item.product_variant_one)[0].variant_title
                // check if the variant title is already exist
                if (productvariantprices.filter((variant) => variant.title === variant_title).length === 0){
                    productvariantprices.push({
                        title: variant_title,
                        price: item.price,
                        stock: item.stock,
                        id: item.id
                    })
                }
            })
            setProductVariantPrices(productvariantprices)

        }
    }, [])


    return (
        <div>
            <section>
                <div className="row">
                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            <div className="card-body">
                                <div className="form-group">
                                    <label htmlFor="">Product Name</label>
                                    <input type="text" placeholder="Product Name" className="form-control" value={productName} onChange={(e) => setProductName(e.target.value)}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Product SKU</label>
                                    <input type="text" placeholder="Product Name" className="form-control" value={productSku} onChange={(e) => setProductSku(e.target.value)}/>
                                </div>
                                <div className="form-group">
                                    <label htmlFor="">Description</label>
                                    <textarea id="" cols="30" rows="4" className="form-control" value={productDescription} onChange={(e) => setProductDescription(e.target.value)}>
                                        
                                    </textarea>
                                </div>
                            </div>
                        </div>

                        <div className="card shadow mb-4">
                            <div
                                className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                <h6 className="m-0 font-weight-bold text-primary">Media</h6>
                            </div>
                            <div className="card-body border">
                                <Dropzone onDrop={acceptedFiles => {
                                    let media = [...productMedia]
                                        acceptedFiles.forEach(async (file) => {
                                        media.push(await getBase64(file))
                                    })
                                    setTimeout(() => {
                                        setProductMedia(media)
                                    }, 1000);
                                }}>
                                    {({getRootProps, getInputProps}) => (
                                        <section>
                                            {productMedia.length > 0 && (
                                                <div className="row">
                                                    {productMedia.map((file, index) => (
                                                        <div className="col-md-3" key={index}>
                                                            <img src={file} alt="" className="img-fluid"
                                                                onDoubleClick={() => {
                                                                    let media = [...productMedia]
                                                                    media.splice(index, 1)
                                                                    setProductMedia(media)
                                                                }}
                                                            />
                                                        </div>
                                                    ))}
                                                    
                                                </div>

                                            )}
                                            <div {...getRootProps()}>
                                                <input {...getInputProps()} />
                                                <p>Drag 'n' drop some files here, or click to select files</p>
                                                <div style={{color:'red', opacity:'.7', marginTop:'-8px'}}>Double click to remove the image</div>
                                            </div>
                                        </section>
                                    )}
                                </Dropzone>
                            </div>
                        </div>
                    </div>

                    <div className="col-md-6">
                        <div className="card shadow mb-4">
                            {!props.edit?(
                                <>
                                    <div className="card-header py-3 d-flex flex-row align-items-center justify-content-between">
                                        <h6 className="m-0 font-weight-bold text-primary">Variants</h6>
                                    </div>
                                    <div className="card-body">

                                        {
                                            productVariants.map((element, index) => {
                                                return (
                                                    <div className="row" key={index}>
                                                        <div className="col-md-4">
                                                            <div className="form-group">
                                                                <label htmlFor="">Option</label>
                                                                <select className="form-control" defaultValue={element.option}>
                                                                    {
                                                                        JSON.parse(props.variants.replaceAll("'", '"')).map((variant, index) => {
                                                                            return (<option key={index}
                                                                                            value={variant.id}>{variant.title}</option>)
                                                                        })
                                                                    }

                                                                </select>
                                                            </div>
                                                        </div>

                                                        <div className="col-md-8">
                                                            <div className="form-group">
                                                                {
                                                                    productVariants.length > 1
                                                                        ? <label htmlFor="" className="float-right text-primary"
                                                                                style={{marginTop: "-30px"}}
                                                                                onClick={() => removeProductVariant(index)}>remove</label>
                                                                        : ''
                                                                }

                                                                <section style={{marginTop: "30px"}}>
                                                                    <TagsInput value={element.tags}
                                                                            style="margin-top:30px"
                                                                            onChange={(value) => handleInputTagOnChange(value, index)}/>
                                                                </section>

                                                            </div>
                                                        </div>
                                                    </div>
                                                )
                                            })
                                        }


                                    </div>
                                    <div className="card-footer">
                                        {productVariants.length !== 3
                                            ? <button className="btn btn-primary" onClick={handleAddClick}>Add another
                                                option</button>
                                            : ''
                                        }

                                    </div>
                                </>
                            ): null}
                            

                            <div className="card-header text-uppercase">Preview</div>
                            <div className="card-body">
                                <div className="table-responsive">
                                    <table className="table">
                                        <thead>
                                        <tr>
                                            <td>Variant</td>
                                            <td>Price</td>
                                            <td>Stock</td>
                                        </tr>
                                        </thead>
                                        <tbody>
                                        {
                                            productVariantPrices.map((productVariantPrice, index) => {
                                                return (
                                                    <tr key={index}>
                                                        <td>{productVariantPrice.title}</td>
                                                        <td>
                                                            <input className="form-control" type="text" value={productVariantPrice.price} onChange={(e) => handlePriceOnChange(e, index)}/>
                                                        </td>
                                                        <td>
                                                            <input className="form-control" type="text" value={productVariantPrice.stock} onChange={(e) => handleStockOnChange(e, index)}/>
                                                        </td>
                                                    </tr>
                                                )
                                            })
                                        }
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <button type="button" onClick={saveProduct} className="btn btn-lg btn-primary red">Save</button>
                <button type="button" className="btn btn-secondary btn-lg">Cancel</button>
            </section>
        </div>
    );
};

export default CreateProduct;
