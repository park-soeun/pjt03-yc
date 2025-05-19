from shiny import App, ui
from htmltools import tags, HTML

kakao_js_key = "3d91fd34529d5628fb6503bc106ebd0d"

app_ui = ui.page_fluid(
    ui.h2("🗺️ 카카오 지도 - 장소 카테고리 검색 예제"),
    ui.navset_tab(
        ui.nav_panel(
            "탭1 - 지도",
            tags.div(
                id="kakao_map1", style="width:100%; height:500px; margin-bottom:10px;"
            ),
            tags.div(
                tags.span("🍽 음식점", id="FD6", **{"data-order": "0"}),
                tags.span("☕ 카페", id="CE7", **{"data-order": "1"}),
                tags.span("🏪 편의점", id="CS2", **{"data-order": "2"}),
                id="category",
                style="margin: 10px; display: flex; gap: 10px; cursor: pointer;",
            ),
        )
    ),
    tags.style(
        """
        #category span {
            padding: 6px 10px;
            background: #eee;
            border: 1px solid #aaa;
            border-radius: 4px;
        }
        #category .on {
            background: #4285f4;
            color: white;
            font-weight: bold;
        }
        .placeinfo_wrap {position:absolute;bottom:28px;left:0;width:250px;z-index:1;}
        .placeinfo {background:#fff;border:1px solid #ccc;border-bottom:2px solid #ddd;padding:10px;font-size:14px;}
        .placeinfo .title {display:block;font-weight:bold;}
        .placeinfo .tel {color:#009900;display:block;margin-top:5px;}
        .jibun {color:#888;font-size:12px;display:block;margin-top:2px;}
    """
    ),
    tags.script(
        HTML(
            f"""
        const script = document.createElement("script");
        script.src = "https://dapi.kakao.com/v2/maps/sdk.js?appkey={kakao_js_key}&libraries=services&autoload=false";
        script.onload = function () {{
            kakao.maps.load(function () {{
                const mapContainer = document.getElementById('kakao_map1');
                const map = new kakao.maps.Map(mapContainer, {{
                    center: new kakao.maps.LatLng(37.566826, 126.9786567),
                    level: 5
                }});
                const ps = new kakao.maps.services.Places(map);

                let placeOverlay = new kakao.maps.CustomOverlay({{zIndex:1}});
                let contentNode = document.createElement('div');
                let markers = [];
                let currCategory = '';

                contentNode.className = 'placeinfo_wrap';
                placeOverlay.setContent(contentNode);
                contentNode.addEventListener('mousedown', kakao.maps.event.preventMap);
                contentNode.addEventListener('touchstart', kakao.maps.event.preventMap);

                kakao.maps.event.addListener(map, 'idle', searchPlaces);

                function addCategoryClickEvent() {{
                    const category = document.getElementById('category');
                    const children = category.children;
                    for (let i = 0; i < children.length; i++) {{
                        children[i].onclick = onClickCategory;
                    }}
                }}

                function onClickCategory() {{
                    const id = this.id;
                    const className = this.className;
                    placeOverlay.setMap(null);
                    if (className === 'on') {{
                        currCategory = '';
                        changeCategoryClass();
                        removeMarker();
                    }} else {{
                        currCategory = id;
                        changeCategoryClass(this);
                        searchPlaces();
                    }}
                }}

                function changeCategoryClass(el) {{
                    const category = document.getElementById('category');
                    const children = category.children;
                    for (let i = 0; i < children.length; i++) {{
                        children[i].className = '';
                    }}
                    if (el) el.className = 'on';
                }}

                function searchPlaces() {{
                    if (!currCategory) return;
                    placeOverlay.setMap(null);
                    removeMarker();
                    ps.categorySearch(currCategory, placesSearchCB, {{useMapBounds:true}});
                }}

                function placesSearchCB(data, status) {{
                    if (status === kakao.maps.services.Status.OK) {{
                        displayPlaces(data);
                    }}
                }}

                function displayPlaces(places) {{
                    const order = document.getElementById(currCategory).getAttribute('data-order');
                    for (let i = 0; i < places.length; i++) {{
                        const marker = addMarker(new kakao.maps.LatLng(places[i].y, places[i].x), order);
                        kakao.maps.event.addListener(marker, 'click', function() {{
                            displayPlaceInfo(places[i]);
                        }});
                    }}
                }}

                function addMarker(position, order) {{
                    const imageSrc = 'https://t1.daumcdn.net/localimg/localimages/07/mapapidoc/places_category.png';
                    const imageSize = new kakao.maps.Size(27, 28);
                    const imgOptions = {{
                        spriteSize: new kakao.maps.Size(72, 208),
                        spriteOrigin: new kakao.maps.Point(46, order * 36),
                        offset: new kakao.maps.Point(11, 28)
                    }};
                    const markerImage = new kakao.maps.MarkerImage(imageSrc, imageSize, imgOptions);
                    const marker = new kakao.maps.Marker({{ position, image: markerImage }});
                    marker.setMap(map);
                    markers.push(marker);
                    return marker;
                }}

                function removeMarker() {{
                    for (let i = 0; i < markers.length; i++) {{
                        markers[i].setMap(null);
                    }}
                    markers = [];
                }}

                function displayPlaceInfo(place) {{
                    let content = '<div class=\"placeinfo\">' +
                                  '<a class=\"title\" href=\"' + place.place_url + '\" target=\"_blank\">' + place.place_name + '</a>';
                    if (place.road_address_name) {{
                        content += '<span>' + place.road_address_name + '</span>' +
                                   '<span class=\"jibun\">(지번 : ' + place.address_name + ')</span>';
                    }} else {{
                        content += '<span>' + place.address_name + '</span>';
                    }}
                    content += '<span class=\"tel\">' + place.phone + '</span>' + '</div><div class=\"after\"></div>';
                    contentNode.innerHTML = content;
                    placeOverlay.setPosition(new kakao.maps.LatLng(place.y, place.x));
                    placeOverlay.setMap(map);
                }}

                addCategoryClickEvent();
            }});
        }};
        document.head.appendChild(script);
    """
        )
    ),
)

app = App(app_ui, server=lambda input, output, session: None)
